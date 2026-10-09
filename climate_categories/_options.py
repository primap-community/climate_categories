"""Categorizations with options.

A categorization with options consists of a base categorization (e.g. ``ISO3``) and
named options (e.g. ``eu`` or ``unfccc``), which are patches to the base
categorization. Options are combined on demand, yielding categorizations named like
``ISO3[eu,unfccc]``. Not all combinations of options are meaningful or
quality-controlled, so each family of categorizations declares the combinations of
options which are not supported. Aliases name commonly used combinations of options,
like ``ISO3_PRIMAP``.
"""

import copy
import dataclasses
import datetime
import functools
import itertools
import pathlib
import re
import typing
import warnings

import strictyaml as sy

from . import _categories

_OPTION_NAME_RE = re.compile(r"[A-Za-z0-9_]+")


class UnsupportedCombinationError(ValueError):
    """The requested combination of options is not quality-controlled.

    Use ``allow_unsupported=True`` to build it anyway."""


class UnsupportedCombinationWarning(UserWarning):
    """A combination of options which is not quality-controlled was built."""


_removal_schema = sy.Map(
    {
        "codes": sy.Seq(sy.Str()),
        sy.Optional("comment"): sy.Str(),
    }
)

_patch_schema = {
    sy.Optional("add_categories"): sy.MapPattern(
        sy.Str(), _categories.HierarchicalCategory._strictyaml_schema
    ),
    sy.Optional("update_categories"): sy.MapPattern(
        sy.Str(),
        sy.Map(
            {
                sy.Optional("title"): sy.Str(),
                sy.Optional("comment"): sy.Str(),
                sy.Optional("info"): sy.MapPattern(sy.Str(), sy.Any()),
            }
        ),
    ),
    sy.Optional("add_alternative_codes"): sy.MapPattern(sy.Str(), sy.Str()),
    sy.Optional("remove_alternative_codes"): sy.MapPattern(sy.Str(), sy.Str()),
    sy.Optional("add_children"): sy.MapPattern(sy.Str(), sy.Seq(sy.Seq(sy.Str()))),
    sy.Optional("remove_children"): sy.MapPattern(sy.Str(), sy.Seq(sy.Seq(sy.Str()))),
    sy.Optional("remove_categories"): _removal_schema,
    sy.Optional("merge_into"): sy.MapPattern(sy.Str(), sy.Str()),
    sy.Optional("split_from"): sy.MapPattern(sy.Str(), sy.Str()),
}


def _all_codes(categories: dict[str, dict]) -> dict[str, str]:
    """Map all codes of the categories in a specification to their primary code."""
    codes = {}
    for code, spec in categories.items():
        codes[code] = code
        for alternative_code in spec.get("alternative_codes", []):
            codes[alternative_code] = code
    return codes


def _descendants(categories: dict[str, dict], code: str) -> set[str]:
    """Primary codes of all descendants of a category in a specification, following
    all child sets."""
    codes = _all_codes(categories)
    descendants: set[str] = set()
    todo = [code]
    while todo:
        for child_set in categories[todo.pop()].get("children", []):
            for child in child_set:
                child = codes.get(child, child)
                if child in categories and child not in descendants:
                    descendants.add(child)
                    todo.append(child)
    return descendants


def _add_to_info_list(
    category_spec: dict[str, typing.Any],
    key: str,
    codes: typing.Iterable[str],
    opposite_key: str,
) -> None:
    """Add codes to the list ``info[key]`` of a category specification.

    Codes which are in ``info[opposite_key]`` cancel out instead, e.g. a category which
    is merged back into the category it was split from. Emptied lists are removed."""
    info = category_spec.setdefault("info", {})
    codes = set(codes)
    opposite = set(info.get(opposite_key, []))
    for k, values in (
        (key, set(info.get(key, [])) | (codes - opposite)),
        (opposite_key, opposite - codes),
    ):
        if values:
            info[k] = sorted(values)
        else:
            info.pop(k, None)
    if not info:
        del category_spec["info"]


def _append_comment(category_spec: dict[str, typing.Any], sentence: str) -> None:
    """Append a sentence to the comment of a category specification."""
    if category_spec.get("comment"):
        category_spec["comment"] += f" {sentence}"
    else:
        category_spec["comment"] = sentence


@dataclasses.dataclass(frozen=True, kw_only=True)
class CategoryRemoval:
    """Removal of categories from a categorization.

    Attributes
    ----------
    codes : tuple of str
        Primary codes of the categories to remove. In categorizations with
        ``total_sum``, all child sets which contained removed categories are dropped
        because they would not add up anymore. Use ``merge_into`` of the patch instead
        if the removed categories are included in other categories.
    comment : str, optional
        Added to the comment of all categories whose children were changed.
    """

    codes: tuple[str, ...]
    comment: str | None = None

    @classmethod
    def from_spec(cls, spec: dict[str, typing.Any]) -> typing.Self:
        return cls(
            codes=tuple(spec["codes"]),
            comment=spec.get("comment"),
        )

    def to_spec(self) -> dict[str, typing.Any]:
        spec: dict[str, typing.Any] = {"codes": list(self.codes)}
        if self.comment is not None:
            spec["comment"] = self.comment
        return spec


@dataclasses.dataclass(frozen=True, kw_only=True)
class CategorizationPatch:
    """Changes to a categorization.

    Patches are applied to the specification of a categorization (see
    ``Categorization.to_spec``) in three phases: first, all changes of all patches
    (everything except splits, merges, and removals of categories) are applied, then
    all splits, then all merges and removals, so that splits, merges, and removals also
    affect categories added by other patches. Within the first phase, each patch adds
    categories, then removes and adds alternative codes, then removes and adds child
    sets, then updates categories, so that alternative codes can be moved to other
    categories and child sets can be replaced in a single patch.

    Attributes
    ----------
    add_categories : dict
        New categories, mapping the primary code to the specification of the category
        like in a categorization file.
    update_categories : dict
        Changes to existing categories, mapping the primary code to a dict with the
        optional keys ``title`` and ``comment``, which replace the title and comment
        of the category, and ``info``, which is added to the info of the category.
    add_alternative_codes : dict
        New alternative codes, mapping the new alternative code to the primary code of
        an existing category.
    remove_alternative_codes : dict
        Alternative codes to remove, mapping the alternative code to the primary code
        of its category. Child sets which use the removed alternative code use the
        primary code instead.
    add_children : dict
        New sets of children, mapping the primary code of a parent category to a list
        of child sets.
    remove_children : dict
        Sets of children to remove, mapping the primary code of a parent category to a
        list of child sets. The order of the children in a set does not matter.
    remove_categories : CategoryRemoval, optional
        Categories to remove.
    merge_into : dict
        Categories to remove because they are included in other categories (e.g.
        the emissions of Palestine are included in the emissions of Israel), mapping
        the primary code of the removed category to the primary code of the category
        it is included in. The removed code is recorded in the ``includes`` info of
        the receiving category. Child sets which also contain the receiving category
        (or one of its ancestors) still add up and only lose the removed category.
        Other child sets which contained the removed category are treated like for
        ``remove_categories``. Merges are applied before ``remove_categories``.
    split_from : dict
        The mirror image of ``merge_into``: categories which are split from other
        categories (e.g. Kosovo is split from Serbia), mapping the primary code of the
        split category to the primary code of the category it is split from. The split
        category has to exist already, usually it is added by ``add_categories``. The
        split code is recorded in the ``excludes`` info of the category it is split
        from. In categorizations with ``total_sum``, the split category is added to all
        child sets which contain the category it is split from, so that they still add
        up. Without ``total_sum``, child sets are not changed.
    """

    add_categories: dict[str, dict] = dataclasses.field(default_factory=dict)
    update_categories: dict[str, dict] = dataclasses.field(default_factory=dict)
    add_alternative_codes: dict[str, str] = dataclasses.field(default_factory=dict)
    remove_alternative_codes: dict[str, str] = dataclasses.field(default_factory=dict)
    add_children: dict[str, list[list[str]]] = dataclasses.field(default_factory=dict)
    remove_children: dict[str, list[list[str]]] = dataclasses.field(
        default_factory=dict
    )
    remove_categories: CategoryRemoval | None = None
    merge_into: dict[str, str] = dataclasses.field(default_factory=dict)
    split_from: dict[str, str] = dataclasses.field(default_factory=dict)

    def _label(self) -> str:
        return "patch"

    @staticmethod
    def _patch_kwargs_from_spec(spec: dict[str, typing.Any]) -> dict[str, typing.Any]:
        kwargs = {
            key: spec[key]
            for key in (
                "add_categories",
                "update_categories",
                "add_alternative_codes",
                "remove_alternative_codes",
                "add_children",
                "remove_children",
                "merge_into",
                "split_from",
            )
            if key in spec
        }
        if "remove_categories" in spec:
            kwargs["remove_categories"] = CategoryRemoval.from_spec(
                spec["remove_categories"]
            )
        return kwargs

    def _patch_to_spec(self) -> dict[str, typing.Any]:
        spec: dict[str, typing.Any] = {}
        for key in (
            "add_categories",
            "update_categories",
            "add_alternative_codes",
            "remove_alternative_codes",
            "add_children",
            "remove_children",
            "merge_into",
            "split_from",
        ):
            value = getattr(self, key)
            if value:
                spec[key] = copy.deepcopy(value)
        if self.remove_categories is not None:
            spec["remove_categories"] = self.remove_categories.to_spec()
        return spec

    def apply_changes(self, spec: dict[str, typing.Any]) -> None:
        """Apply all changes of this patch except splits, merges, and removals of
        categories to the categorization specification."""
        categories = spec["categories"]
        hierarchical = spec["hierarchical"]
        codes = _all_codes(categories)

        for code, category_spec in self.add_categories.items():
            new_codes = [code, *category_spec.get("alternative_codes", [])]
            existing = [c for c in new_codes if c in codes]
            if existing:
                raise ValueError(
                    f"{self._label()} adds the category {code!r}, but the codes "
                    f"{existing!r} already exist."
                )
            if "children" in category_spec and not hierarchical:
                raise ValueError(
                    f"{self._label()} adds children to {code!r}, but the "
                    "categorization is not hierarchical."
                )
            categories[code] = copy.deepcopy(category_spec)
            for new_code in new_codes:
                codes[new_code] = code

        for alternative_code, primary_code in self.remove_alternative_codes.items():
            if primary_code not in categories:
                raise ValueError(
                    f"{self._label()} removes the alternative code "
                    f"{alternative_code!r} of {primary_code!r}, which is not a "
                    "primary code."
                )
            alternative_codes = categories[primary_code].get("alternative_codes", [])
            if alternative_code not in alternative_codes:
                raise ValueError(
                    f"{self._label()} removes the alternative code "
                    f"{alternative_code!r} of {primary_code!r}, but it is not an "
                    f"alternative code of {primary_code!r}."
                )
            alternative_codes.remove(alternative_code)
            if not alternative_codes:
                del categories[primary_code]["alternative_codes"]
            del codes[alternative_code]
            # the category still exists, so use its primary code instead
            for category_spec in categories.values():
                for child_set in category_spec.get("children", []):
                    child_set[:] = [
                        primary_code if c == alternative_code else c for c in child_set
                    ]
            if spec.get("canonical_top_level_category") == alternative_code:
                spec["canonical_top_level_category"] = primary_code

        for alternative_code, primary_code in self.add_alternative_codes.items():
            if alternative_code in codes:
                raise ValueError(
                    f"{self._label()} adds the alternative code {alternative_code!r},"
                    " but it already exists."
                )
            if primary_code not in categories:
                raise ValueError(
                    f"{self._label()} adds the alternative code {alternative_code!r} "
                    f"to {primary_code!r}, which is not a primary code."
                )
            categories[primary_code].setdefault("alternative_codes", []).append(
                alternative_code
            )
            codes[alternative_code] = primary_code

        for parent, child_sets in self.remove_children.items():
            if not hierarchical:
                raise ValueError(
                    f"{self._label()} removes children of {parent!r}, but the "
                    "categorization is not hierarchical."
                )
            if parent not in categories:
                raise ValueError(
                    f"{self._label()} removes children of {parent!r}, which is not a "
                    "primary code."
                )
            existing_sets = categories[parent].get("children", [])
            for child_set in child_sets:
                wanted = {codes.get(c, c) for c in child_set}
                matching = [
                    i
                    for i, existing in enumerate(existing_sets)
                    if {codes.get(c, c) for c in existing} == wanted
                ]
                if not matching:
                    raise ValueError(
                        f"{self._label()} removes the children {list(child_set)!r} "
                        f"of {parent!r}, but {parent!r} has no such child set."
                    )
                del existing_sets[matching[0]]
            if not existing_sets:
                categories[parent].pop("children", None)

        for parent, child_sets in self.add_children.items():
            if not hierarchical:
                raise ValueError(
                    f"{self._label()} adds children to {parent!r}, but the "
                    "categorization is not hierarchical."
                )
            if parent not in categories:
                raise ValueError(
                    f"{self._label()} adds children to {parent!r}, which is not a "
                    "primary code."
                )
            categories[parent].setdefault("children", []).extend(
                list(child_set) for child_set in child_sets
            )

        for code, update in self.update_categories.items():
            if code not in categories:
                raise ValueError(
                    f"{self._label()} updates {code!r}, which is not a primary code."
                )
            category_spec = categories[code]
            for key in ("title", "comment"):
                if key in update:
                    category_spec[key] = update[key]
            if "info" in update:
                category_spec.setdefault("info", {}).update(
                    copy.deepcopy(update["info"])
                )

    def apply_splits(self, spec: dict[str, typing.Any]) -> None:
        """Apply all splits of this patch to the categorization specification."""
        if not self.split_from:
            return
        categories = spec["categories"]
        removal = self.remove_categories
        removed = {*self.merge_into, *(removal.codes if removal is not None else ())}

        for code, source in self.split_from.items():
            for c in (code, source):
                if c not in categories:
                    raise ValueError(
                        f"{self._label()} splits {code!r} from {source!r}, but {c!r} "
                        "is not a primary code."
                    )
                if c in removed:
                    raise ValueError(
                        f"{self._label()} splits {code!r} from {source!r}, but {c!r} "
                        "is removed."
                    )
            if code == source:
                raise ValueError(f"{self._label()} splits {code!r} from itself.")
            codes = {code, *categories[code].get("alternative_codes", [])}
            if spec.get("canonical_top_level_category") in codes:
                raise ValueError(
                    f"{self._label()} splits {code!r}, which is the canonical top "
                    "level category."
                )

        for code, source in self.split_from.items():
            spec_a = categories[code]
            spec_b = categories[source]
            _add_to_info_list(
                spec_b,
                "excludes",
                [code, *spec_a.get("info", {}).get("includes", [])],
                "includes",
            )
            _append_comment(spec_b, f"Excludes {code} ({spec_a['title']}).")

        if not spec.get("total_sum", False):
            return
        primary = _all_codes(categories)
        for category_spec in categories.values():
            changed = {}
            for child_set in category_spec.get("children", []):
                child_set_primary = {primary.get(c, c) for c in child_set}
                for code, source in self.split_from.items():
                    if source in child_set_primary and code not in child_set_primary:
                        child_set.append(code)
                        child_set_primary.add(code)
                        changed[code] = source
            for code, source in changed.items():
                _append_comment(
                    category_spec,
                    f"{code} ({categories[code]['title']}) is split from "
                    f"{source} ({categories[source]['title']}).",
                )

    def apply_removals(self, spec: dict[str, typing.Any]) -> None:
        """Apply all removals and merges of this patch to the categorization
        specification."""
        removal = self.remove_categories
        removed = removal.codes if removal is not None else ()
        if not removed and not self.merge_into:
            return
        categories = spec["categories"]

        for code in (*self.merge_into, *removed):
            if code not in categories:
                raise ValueError(
                    f"{self._label()} removes {code!r}, which is not a primary code."
                )
            codes = {code, *categories[code].get("alternative_codes", [])}
            if spec.get("canonical_top_level_category") in codes:
                raise ValueError(
                    f"{self._label()} removes {code!r}, which is the canonical top "
                    "level category."
                )
        for code, target in self.merge_into.items():
            if code in removed:
                raise ValueError(
                    f"{self._label()} removes {code!r} and also merges it into "
                    f"{target!r}."
                )
            if target not in categories:
                raise ValueError(
                    f"{self._label()} merges {code!r} into {target!r}, which is not "
                    "a primary code."
                )
            if target in self.merge_into or target in removed:
                raise ValueError(
                    f"{self._label()} merges {code!r} into {target!r}, which is "
                    "removed itself."
                )

        # removed code (primary or alternative) -> merge target or None
        removed_codes: dict[str, str | None] = {}
        # parent comments, by removed primary code
        comments: dict[str, str | None] = {}
        for code, target in self.merge_into.items():
            spec_a = categories[code]
            spec_b = categories[target]
            _add_to_info_list(
                spec_b,
                "includes",
                [code, *spec_a.get("info", {}).get("includes", [])],
                "excludes",
            )
            _append_comment(spec_b, f"Includes {code} ({spec_a['title']}).")
            comments[code] = (
                f"{code} ({spec_a['title']}) is included in {target} "
                f"({spec_b['title']})."
            )
        for code in removed:
            comments[code] = removal.comment
        for code in comments:
            target = self.merge_into.get(code)
            for c in (code, *categories[code].get("alternative_codes", [])):
                removed_codes[c] = target
        primary = _all_codes(categories)
        for code in comments:
            del categories[code]

        drop_sets = spec.get("total_sum", False)
        descendants: dict[str, set[str]] = {}

        def still_adds_up(child_set: list[str], removed_code: str) -> bool:
            target = removed_codes[removed_code]
            if target is None:
                return False
            for child in child_set:
                child = primary.get(child, child)
                if child == target:
                    return True
                if child not in categories:
                    continue
                if child not in descendants:
                    descendants[child] = _descendants(categories, child)
                if target in descendants[child]:
                    return True
            return False

        for category_spec in categories.values():
            changed = [
                primary[child]
                for child_set in category_spec.get("children", [])
                for child in child_set
                if child in removed_codes
            ]
            if not changed:
                continue
            new_children = []
            for child_set in category_spec["children"]:
                gone = [child for child in child_set if child in removed_codes]
                if gone:
                    if drop_sets and not all(
                        still_adds_up(child_set, child) for child in gone
                    ):
                        continue
                    child_set = [c for c in child_set if c not in removed_codes]
                if child_set and sorted(child_set) not in (
                    sorted(c) for c in new_children
                ):
                    new_children.append(child_set)
            if new_children:
                category_spec["children"] = new_children
            else:
                del category_spec["children"]
            for code in dict.fromkeys(changed):
                comment = comments[code]
                if comment is not None:
                    _append_comment(category_spec, comment)


@dataclasses.dataclass(frozen=True, kw_only=True)
class CategorizationOption(CategorizationPatch):
    """An option of a categorization, i.e. a named patch of the base categorization.

    Attributes
    ----------
    name : str
        The name of the option, like ``eu``.
    title : str
        A short, descriptive title for humans.
    comment : str
        Notes and explanations for humans.
    references : str
        Citable reference(s) for the data added by the option.
    last_update : datetime.date
        The date of the last change.
    requires : tuple of str
        Options which have to be enabled together with this option.
    conflicts : tuple of str
        Options which can not be enabled together with this option.
    base : str, optional
        The categorization the option is meant to be applied to, like
        ``ISO3_PRIMAP``. Used by ``load_extension`` for options which are not part of
        the options of a categorization included in climate_categories.
    """

    name: str
    title: str
    comment: str = ""
    references: str = ""
    last_update: datetime.date
    requires: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ()
    base: str | None = None

    _strictyaml_schema: typing.ClassVar = sy.Map(
        {
            "option": sy.Str(),
            sy.Optional("base"): sy.Str(),
            "title": sy.Str(),
            sy.Optional("comment"): sy.Str(),
            sy.Optional("references"): sy.Str(),
            "last_update": sy.Str(),
            sy.Optional("requires"): sy.Seq(sy.Str()),
            sy.Optional("conflicts"): sy.Seq(sy.Str()),
            **_patch_schema,
        }
    )

    def __post_init__(self):
        if not _OPTION_NAME_RE.fullmatch(self.name) or self.name == "options":
            raise ValueError(
                f"Invalid option name {self.name!r}, option names may only contain "
                "letters, digits and underscores, and 'options' is reserved."
            )

    def _label(self) -> str:
        return f"Option {self.name!r}"

    @classmethod
    def from_spec(cls, spec: dict[str, typing.Any]) -> typing.Self:
        """Create option from a dictionary specification."""
        return cls(
            name=spec["option"],
            title=spec["title"],
            comment=spec.get("comment", ""),
            references=spec.get("references", ""),
            last_update=datetime.date.fromisoformat(spec["last_update"]),
            requires=tuple(spec.get("requires", ())),
            conflicts=tuple(spec.get("conflicts", ())),
            base=spec.get("base"),
            **cls._patch_kwargs_from_spec(spec),
        )

    def to_spec(self) -> dict[str, typing.Any]:
        """Turn this option into a specification dictionary ready to be written to a
        yaml file."""
        spec: dict[str, typing.Any] = {"option": self.name}
        if self.base is not None:
            spec["base"] = self.base
        spec["title"] = self.title
        if self.comment:
            spec["comment"] = self.comment
        if self.references:
            spec["references"] = self.references
        spec["last_update"] = self.last_update.isoformat()
        if self.requires:
            spec["requires"] = list(self.requires)
        if self.conflicts:
            spec["conflicts"] = list(self.conflicts)
        spec.update(self._patch_to_spec())
        return spec

    @classmethod
    def from_yaml(cls, filepath: str | pathlib.Path | typing.TextIO) -> typing.Self:
        """Read option from a StrictYaml file."""
        return cls.from_spec(_categories._read_yaml(filepath, cls._strictyaml_schema))

    @classmethod
    def from_python(cls, filepath: str | pathlib.Path | typing.TextIO) -> typing.Self:
        """Read option from a python cache file written by to_python.

        Note that this executes the python cache file. Only load from python cache
        files you trust."""
        return cls.from_spec(_categories._read_python(filepath))

    def to_yaml(self, filepath: str | pathlib.Path) -> None:
        """Write to a YAML file."""
        _categories._write_yaml(self.to_spec(), filepath)

    def to_python(self, filepath: str | pathlib.Path) -> None:
        """Write spec to a Python file."""
        _categories._write_python(self.to_spec(), filepath)


@dataclasses.dataclass(frozen=True, kw_only=True)
class OptionCombination(CategorizationPatch):
    """A patch which is applied when all of the given options are enabled.

    Used to handle the interaction of options.

    Attributes
    ----------
    options : tuple of str
        The options which all have to be enabled for the patch to be applied.
    comment : str
        Notes and explanations for humans, added to the comment of the categorization.
    """

    options: tuple[str, ...]
    comment: str = ""

    _strictyaml_schema: typing.ClassVar = sy.Map(
        {
            "options": sy.Seq(sy.Str()),
            sy.Optional("comment"): sy.Str(),
            **_patch_schema,
        }
    )

    def _label(self) -> str:
        return f"Combination of options {list(self.options)!r}"

    @classmethod
    def from_spec(cls, spec: dict[str, typing.Any]) -> typing.Self:
        return cls(
            options=tuple(sorted(spec["options"])),
            comment=spec.get("comment", ""),
            **cls._patch_kwargs_from_spec(spec),
        )

    def to_spec(self) -> dict[str, typing.Any]:
        spec: dict[str, typing.Any] = {"options": sorted(self.options)}
        if self.comment:
            spec["comment"] = self.comment
        spec.update(self._patch_to_spec())
        return spec


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnsupportedCombination:
    """A combination of options which is not quality-controlled.

    All combinations which contain all of the options are not supported.

    Attributes
    ----------
    options : tuple of str
        The options which together are not supported.
    comment : str
        Why the combination is not supported, for humans.
    """

    options: tuple[str, ...]
    comment: str = ""

    _strictyaml_schema: typing.ClassVar = sy.Map(
        {"options": sy.Seq(sy.Str()), sy.Optional("comment"): sy.Str()}
    )

    @classmethod
    def from_spec(cls, spec: dict[str, typing.Any]) -> typing.Self:
        return cls(
            options=tuple(sorted(spec["options"])), comment=spec.get("comment", "")
        )

    def to_spec(self) -> dict[str, typing.Any]:
        spec: dict[str, typing.Any] = {"options": sorted(self.options)}
        if self.comment:
            spec["comment"] = self.comment
        return spec


@dataclasses.dataclass(frozen=True, kw_only=True)
class OptionManifest:
    """Declaration of the options of a categorization.

    Attributes
    ----------
    base : str
        Name of the base categorization.
    options : tuple of str
        Names of all options, in the order in which they are applied.
    combinations : tuple of OptionCombination
        Patches which handle the interaction of options.
    unsupported : tuple of UnsupportedCombination
        Combinations of options which are not quality-controlled. All other valid
        combinations of options, i.e. combinations which contain all required options
        and no conflicting options, are supported.
    aliases : dict
        Names for commonly used combinations of options, mapping the alias to the
        options.
    """

    base: str
    options: tuple[str, ...]
    combinations: tuple[OptionCombination, ...] = ()
    unsupported: tuple[UnsupportedCombination, ...] = ()
    aliases: dict[str, tuple[str, ...]] = dataclasses.field(default_factory=dict)

    _strictyaml_schema: typing.ClassVar = sy.Map(
        {
            "base": sy.Str(),
            "options": sy.Seq(sy.Str()),
            sy.Optional("combinations"): sy.Seq(OptionCombination._strictyaml_schema),
            sy.Optional("unsupported"): sy.Seq(
                UnsupportedCombination._strictyaml_schema
            ),
            sy.Optional("aliases"): sy.MapPattern(sy.Str(), sy.Seq(sy.Str())),
        }
    )

    @classmethod
    def from_spec(cls, spec: dict[str, typing.Any]) -> typing.Self:
        """Create manifest from a dictionary specification."""
        return cls(
            base=spec["base"],
            options=tuple(spec["options"]),
            combinations=tuple(
                OptionCombination.from_spec(c) for c in spec.get("combinations", [])
            ),
            unsupported=tuple(
                UnsupportedCombination.from_spec(u) for u in spec.get("unsupported", [])
            ),
            aliases={
                alias: tuple(sorted(options))
                for alias, options in spec.get("aliases", {}).items()
            },
        )

    def to_spec(self) -> dict[str, typing.Any]:
        """Turn this manifest into a specification dictionary ready to be written to a
        yaml file."""
        spec: dict[str, typing.Any] = {"base": self.base, "options": list(self.options)}
        if self.combinations:
            spec["combinations"] = [c.to_spec() for c in self.combinations]
        if self.unsupported:
            spec["unsupported"] = [u.to_spec() for u in self.unsupported]
        if self.aliases:
            spec["aliases"] = {
                alias: sorted(options) for alias, options in self.aliases.items()
            }
        return spec

    @classmethod
    def from_yaml(cls, filepath: str | pathlib.Path | typing.TextIO) -> typing.Self:
        """Read manifest from a StrictYaml file."""
        return cls.from_spec(_categories._read_yaml(filepath, cls._strictyaml_schema))

    @classmethod
    def from_python(cls, filepath: str | pathlib.Path | typing.TextIO) -> typing.Self:
        """Read manifest from a python cache file written by to_python.

        Note that this executes the python cache file. Only load from python cache
        files you trust."""
        return cls.from_spec(_categories._read_python(filepath))

    def to_yaml(self, filepath: str | pathlib.Path) -> None:
        """Write to a YAML file."""
        _categories._write_yaml(self.to_spec(), filepath)

    def to_python(self, filepath: str | pathlib.Path) -> None:
        """Write spec to a Python file."""
        _categories._write_python(self.to_spec(), filepath)


def manifest_stem(base: str) -> str:
    """The file name (without extension) of the manifest of the given base."""
    return f"{base}__options"


def option_stem(base: str, option: str) -> str:
    """The file name (without extension) of the given option of the given base."""
    return f"{base}__{option}"


class OptionFamily:
    """A base categorization together with its options.

    Use ``get`` to get the base categorization with options enabled.

    Attributes
    ----------
    base : Categorization
        The base categorization.
    manifest : OptionManifest
        The declaration of the options, their combinations and aliases.
    options : dict
        All options by name, in the order in which they are applied.
    """

    def __init__(
        self,
        *,
        base: "_categories.Categorization",
        manifest: OptionManifest,
        options: dict[str, CategorizationOption],
    ):
        if manifest.base != base.name:
            raise ValueError(
                f"Manifest is for {manifest.base!r}, but the base is {base.name!r}."
            )
        if len(set(manifest.options)) != len(manifest.options):
            raise ValueError(f"{base.name}: options listed multiple times.")
        if set(options) != set(manifest.options):
            raise ValueError(
                f"{base.name}: the given options {sorted(options)!r} do not match "
                f"the options of the manifest {sorted(manifest.options)!r}."
            )
        for name, option in options.items():
            if option.name != name:
                raise ValueError(f"Option {option.name!r} given as {name!r}.")

        self.base = base
        self.manifest = manifest
        self.options = {name: options[name] for name in manifest.options}
        self._cache: dict[str, _categories.Categorization] = {}

        for option in self.options.values():
            for other in (*option.requires, *option.conflicts):
                if other not in self.options or other == option.name:
                    raise ValueError(
                        f"{base.name}: option {option.name!r} requires or conflicts "
                        f"with the invalid option {other!r}."
                    )
        for combination in manifest.combinations:
            self._check_known(combination.options)
            if len(combination.options) < 2:
                raise ValueError(
                    f"{base.name}: combinations need at least two options, not "
                    f"{list(combination.options)!r}."
                )
        for unsupported in manifest.unsupported:
            self._check_known(unsupported.options)
            if not unsupported.options:
                raise ValueError(
                    f"{base.name}: unsupported combinations need at least one option."
                )
        for alias, alias_options in manifest.aliases.items():
            if _categories.parse_name(alias)[1] or alias == base.name:
                raise ValueError(f"{base.name}: invalid alias name {alias!r}.")
            if not self.is_supported(alias_options):
                raise ValueError(
                    f"{base.name}: the options {list(alias_options)!r} of the alias "
                    f"{alias!r} are not a supported combination."
                )

    @classmethod
    def from_yaml(
        cls,
        manifest_path: str | pathlib.Path,
        base: "_categories.Categorization | None" = None,
    ) -> typing.Self:
        """Read the options of a categorization from StrictYaml files.

        The options are read from the files ``{base}__{option}.yaml`` next to the
        manifest file ``{base}__options.yaml``.

        Parameters
        ----------
        manifest_path : str or Path
            Path to the manifest file.
        base : Categorization, optional
            The base categorization. If not given, it is read from ``{base}.yaml``
            next to the manifest file.
        """
        manifest_path = pathlib.Path(manifest_path)
        directory = manifest_path.parent
        manifest = OptionManifest.from_yaml(manifest_path)
        if base is None:
            base = _categories.from_yaml(directory / f"{manifest.base}.yaml")
        options = {
            name: CategorizationOption.from_yaml(
                directory / f"{option_stem(manifest.base, name)}.yaml"
            )
            for name in manifest.options
        }
        return cls(base=base, manifest=manifest, options=options)

    @property
    def name(self) -> str:
        """The name of the base categorization."""
        return self.base.name

    @property
    def aliases(self) -> dict[str, tuple[str, ...]]:
        """Names for commonly used combinations of options."""
        return self.manifest.aliases

    @functools.cached_property
    def supported_combinations(self) -> list[tuple[str, ...]]:
        """All supported combinations of options, including the empty combination.

        These are all combinations which contain all required options, no
        conflicting options, and are not declared unsupported in the manifest.
        """
        combinations = []
        for n in range(len(self.options) + 1):
            for options in itertools.combinations(sorted(self.options), n):
                try:
                    if self.is_supported(options):
                        combinations.append(options)
                except ValueError:
                    # missing required or conflicting options
                    continue
        return combinations

    def _check_known(self, options: typing.Iterable[str]) -> None:
        unknown = [option for option in options if option not in self.options]
        if unknown:
            raise ValueError(
                f"Unknown options {unknown!r} for {self.name}, available options: "
                f"{list(self.options)!r}."
            )

    def check(self, options: typing.Iterable[str]) -> tuple[str, ...]:
        """Check that the options are valid, i.e. are known, have all required options
        and don't conflict.

        Returns
        -------
        options : tuple of str
            The options, sorted.
        """
        options = _categories._options_list(options)
        if len(set(options)) != len(options):
            raise ValueError(f"Options given multiple times: {options!r}.")
        self._check_known(options)
        for name in options:
            option = self.options[name]
            missing = [x for x in option.requires if x not in options]
            if missing:
                raise ValueError(
                    f"Option {name!r} of {self.name} requires the options {missing!r}."
                )
            conflicting = [x for x in option.conflicts if x in options]
            if conflicting:
                raise ValueError(
                    f"Option {name!r} of {self.name} conflicts with the options "
                    f"{conflicting!r}."
                )
        return tuple(sorted(options))

    def _unsupported_by(
        self, options: typing.Iterable[str]
    ) -> UnsupportedCombination | None:
        """The declared unsupported combination which the options contain, if any."""
        options = set(options)
        for unsupported in self.manifest.unsupported:
            if set(unsupported.options) <= options:
                return unsupported
        return None

    def is_supported(self, options: typing.Iterable[str]) -> bool:
        """Is the combination of options quality-controlled?

        Raises a ValueError if the options are not valid at all."""
        return self._unsupported_by(self.check(options)) is None

    def resolve(self, name: str) -> tuple[str, ...] | None:
        """The options of the given alias or name like ``ISO3[eu,unfccc]``.

        Returns None if the name does not belong to this family."""
        if name in self.aliases:
            return self.aliases[name]
        family, options = _categories.parse_name(name)
        if family == self.name:
            return options
        return None

    def get(
        self,
        options: typing.Iterable[str],
        *,
        allow_unsupported: bool = False,
        name: str | None = None,
    ) -> "_categories.Categorization":
        """Get the base categorization with the given options enabled.

        Supported combinations are only built once and cached.

        Parameters
        ----------
        options : iterable of str
            The names of the options to enable.
        allow_unsupported : bool, default False
            Combinations of options which are not supported raise an
            ``UnsupportedCombinationError``. If True, build them anyway, emitting an
            ``UnsupportedCombinationWarning``.
        name : str, optional
            The name of the returned categorization, used for aliases. Defaults to
            the canonical name like ``ISO3[eu,unfccc]``.
        """
        options = self.check(options)
        if not options and name is None:
            return self.base
        if name is None:
            name = _categories.canonical_name(self.name, options)

        unsupported = self._unsupported_by(options)
        if unsupported is not None:
            if not allow_unsupported:
                reason = f" ({unsupported.comment})" if unsupported.comment else ""
                raise UnsupportedCombinationError(
                    f"The combination of options {list(options)!r} of {self.name} is "
                    "not quality-controlled because the options "
                    f"{list(unsupported.options)!r} are not supported together"
                    f"{reason}. Use allow_unsupported=True to use it anyway."
                )
            warnings.warn(
                f"The combination of options {list(options)!r} of {self.name} is not "
                "quality-controlled.",
                UnsupportedCombinationWarning,
                stacklevel=2,
            )
            return self.build(options, name=name)

        if name not in self._cache:
            self._cache[name] = self.build(options, name=name)
        return self._cache[name]

    def build(
        self, options: typing.Iterable[str], *, name: str | None = None
    ) -> "_categories.Categorization":
        """Build the base categorization with the given options enabled.

        Unlike ``get``, this does not check if the combination of options is
        supported and always builds a new categorization.
        """
        options = self.check(options)
        enabled = [option for name, option in self.options.items() if name in options]
        combinations = [
            c for c in self.manifest.combinations if set(c.options) <= set(options)
        ]
        spec = _patched_spec(
            self.base,
            enabled,
            combinations,
            description=f"the options {list(options)!r} of {self.name}",
        )
        if name is None:
            name = _categories.canonical_name(self.name, options)
        spec["name"] = name
        categorization = type(self.base).from_spec(spec)
        # for aliases, the family and options can't be derived from the name.
        categorization.family = self.name
        categorization.enabled_options = options
        categorization._cats = self.base._cats
        categorization._option_family = self
        return categorization


def _patched_spec(
    categorization: "_categories.Categorization",
    options: list["CategorizationOption"],
    combinations: list["OptionCombination"] = (),
    *,
    description: str,
) -> dict[str, typing.Any]:
    """The specification of the categorization with the options and combinations
    applied, including the metadata. The name is left unchanged.

    ``description`` describes the applied options for error messages.
    """
    patches: list[CategorizationPatch] = [*options, *combinations]

    spec = copy.deepcopy(categorization.to_spec())
    for patch in patches:
        patch.apply_changes(spec)
    for patch in patches:
        patch.apply_splits(spec)
    for patch in patches:
        patch.apply_removals(spec)

    codes = _all_codes(spec["categories"])
    for code, category_spec in spec["categories"].items():
        for child_set in category_spec.get("children", []):
            missing = [child for child in child_set if child not in codes]
            if missing:
                raise ValueError(
                    f"Children {missing!r} of {code!r} don't exist after applying "
                    f"{description}."
                )

    if options:
        spec["title"] = (
            f"{categorization.title} with {', '.join(o.title for o in options)}"
        )
    for option in options:
        if option.comment:
            spec["comment"] += f"\n\nOption {option.name!r}: {option.comment}"
    for combination in combinations:
        if combination.comment:
            spec["comment"] += (
                f"\n\nOptions {', '.join(combination.options)} combined: "
                f"{combination.comment}"
            )
    spec["references"] = ";\n".join(
        references.strip().rstrip(";")
        for references in (
            categorization.references,
            *(option.references for option in options),
        )
        if references.strip()
    )
    spec["last_update"] = max(
        [categorization.last_update, *(option.last_update for option in options)]
    ).isoformat()
    return spec


def apply_option(
    categorization: "_categories.Categorization",
    option: "CategorizationOption | str | pathlib.Path",
    *,
    name: str | None = None,
) -> "_categories.Categorization":
    """Apply an option to a categorization, see ``Categorization.apply``."""
    if not isinstance(option, CategorizationOption):
        option = CategorizationOption.from_yaml(option)

    enabled = set(categorization.enabled_options)
    if option.name in enabled:
        raise ValueError(
            f"Option {option.name!r} is already enabled in {categorization.name}."
        )
    missing = [x for x in option.requires if x not in enabled]
    if missing:
        raise ValueError(
            f"Option {option.name!r} requires the options {missing!r}, which are not "
            f"enabled in {categorization.name}."
        )
    conflicting = [x for x in option.conflicts if x in enabled]
    if conflicting:
        raise ValueError(
            f"Option {option.name!r} conflicts with the options {conflicting!r}, "
            f"which are enabled in {categorization.name}."
        )

    spec = _patched_spec(
        categorization,
        [option],
        description=f"the option {option.name!r} to {categorization.name}",
    )
    spec["name"] = f"{categorization.name}_{option.name}" if name is None else name
    result = type(categorization).from_spec(spec)
    result._cats = categorization._cats
    # keep the categories comparable to the categories of the original categorization
    # and its family. This is possible because the family is not part of the hash.
    result.family = categorization.family
    result._canonical_name = result.name
    # later options can require or conflict with this option
    result.enabled_options = tuple(sorted({*enabled, option.name}))
    return result


def load_extension(
    filepath: str
    | pathlib.Path
    | typing.TextIO
    | typing.Sequence[str | pathlib.Path | typing.TextIO],
    cats: "dict[str, _categories.Categorization] | None" = None,
    *,
    name: str | None = None,
) -> "_categories.Categorization":
    """Read options from files and apply them to the categorization they are for.

    The option files have to name the categorization they are for in their ``base``
    field, like ``ISO3_PRIMAP`` or ``ISO3[eu,unfccc]``. Several option files which
    extend the same categorization can be given, they are applied in the given order.
    Later options can require earlier options using ``requires``.

    Parameters
    ----------
    filepath : str, Path, file, or list of them
        The option file(s) in StrictYaml format.
    cats : dict, optional
        The categorizations to look up the base in, by default all categorizations
        included in climate_categories.
    name : str, optional
        The name of the returned categorization, by default ``{base}_{option}`` for a
        single option and ``{base}_{option1}_{option2}`` etc. for several options.

    Returns
    -------
    categorization : Categorization
        The base categorization with the option(s) applied.
    """
    filepaths = filepath if isinstance(filepath, list | tuple) else [filepath]
    if not filepaths:
        raise ValueError("No option files given.")
    options = [CategorizationOption.from_yaml(path) for path in filepaths]
    for option in options:
        if option.base is None:
            raise ValueError(
                f"Option {option.name!r} does not name the categorization it is for "
                "in its 'base' field, use Categorization.apply instead."
            )
    bases = {option.base for option in options}
    if len(bases) > 1:
        raise ValueError(
            f"The options are for different categorizations {sorted(bases)!r}, "
            "extensions which are applied together have to name the same 'base' and "
            "can refer to each other using 'requires'."
        )
    if cats is None:
        import climate_categories

        cats = climate_categories.cats
    categorization = cats[options[0].base]
    for i, option in enumerate(options):
        last = i == len(options) - 1
        categorization = apply_option(
            categorization, option, name=name if last else None
        )
    return categorization


class CategorizationRegistry(dict):
    """All categorizations, by name.

    Categorizations with options, like ``ISO3[eu,unfccc]``, and aliases, like
    ``ISO3_PRIMAP``, are built on first access. Note that iterating over the registry
    only yields categorizations which were already built.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.families: dict[str, OptionFamily] = {}

    def register_family(self, family: OptionFamily) -> None:
        """Register the options of a base categorization."""
        if family.name in self.families:
            raise ValueError(f"Options for {family.name} already registered.")
        for alias in family.aliases:
            if dict.__contains__(self, alias) or any(
                alias in f.aliases for f in self.families.values()
            ):
                raise ValueError(f"Alias {alias!r} already exists.")
        self.families[family.name] = family
        family.base._option_family = family
        family.base._cats = self
        dict.__setitem__(self, family.name, family.base)

    def _resolve(self, name: str) -> tuple[OptionFamily, tuple[str, ...]] | None:
        for family in self.families.values():
            options = family.resolve(name)
            if options is not None:
                return family, options
        return None

    def __missing__(self, name: str) -> "_categories.Categorization":
        resolved = self._resolve(name)
        if resolved is None:
            raise KeyError(name)
        family, options = resolved
        alias = name if name in family.aliases else None
        categorization = family.get(options, name=alias)
        dict.__setitem__(self, categorization.name, categorization)
        return categorization

    def __contains__(self, name: object) -> bool:
        if dict.__contains__(self, name):
            return True
        if not isinstance(name, str):
            return False
        resolved = self._resolve(name)
        if resolved is None:
            return False
        family, options = resolved
        try:
            return family.is_supported(options)
        except ValueError:
            return False

    def get(self, name, default=None):
        """Get the categorization with the given name, or default if it does not
        exist.

        Raises an UnsupportedCombinationError for unsupported combinations of
        options."""
        try:
            return self[name]
        except KeyError:
            return default
