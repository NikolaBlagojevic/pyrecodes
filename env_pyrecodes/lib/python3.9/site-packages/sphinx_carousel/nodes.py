"""Docutils nodes."""
# pylint: disable=keyword-arg-before-vararg
from abc import ABCMeta, abstractmethod
from typing import Dict, List, Optional, Union

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.writers.html5 import HTML5Translator


class BaseNode(nodes.Element, nodes.General):
    """Base node class."""

    CLASSES = []

    def classes(self, *classes_in: Optional[List[str]], join: bool = True) -> Union[str, List[str]]:
        """Return prefixed classes.

        1. If a class starts with "*" then it will not be prefixed and the leading character will be removed.
        2. If no input classes are provided then this defaults to self.CLASSES.
        3. Multiple groups of classes will be flattened into one list.

        :param join: Return a space delimited joined string instead of list of strings.
        """
        prefix = getattr(self, "prefix", "")
        flattened = [
            f"{c[1:]}" if c.startswith("*") else f"{prefix}{c}" for g in (classes_in or [self.CLASSES]) if g for c in g
        ]
        return " ".join(flattened) if join else flattened

    @staticmethod
    @abstractmethod
    def html_visit(writer: HTML5Translator, node: "BaseNode"):
        """Append opening tags to document body list."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def html_depart(writer: HTML5Translator, _):
        """Append closing tags to document body list."""
        raise NotImplementedError

    @classmethod
    def add_node(cls, app: Sphinx):
        """Convenience method that adds the subclass node to the Sphinx app.."""
        app.add_node(
            cls,
            html=(cls.html_visit, cls.html_depart),
            latex=(lambda *_: None, lambda *_: None),  # TODO https://github.com/Robpol86/sphinx-carousel/issues/50
            man=(lambda *_: None, lambda *_: None),  # TODO https://github.com/Robpol86/sphinx-carousel/issues/51
            texinfo=(lambda *_: None, lambda *_: None),  # TODO https://github.com/Robpol86/sphinx-carousel/issues/51
            text=(lambda *_: None, lambda *_: None),  # TODO https://github.com/Robpol86/sphinx-carousel/issues/51
        )


class CarouselMainNode(BaseNode):
    """Main div."""

    CLASSES = ["carousel", "slide"]
    CLASSES_DARK = ["carousel-dark"]
    CLASSES_FADE = ["carousel-fade"]

    def __init__(
        self,
        *args,
        div_id: str = "",
        prefix: str = "",
        attributes: Dict[str, str] = None,
        fade: bool = False,
        dark: bool = False,
        **kwargs,
    ):
        """Constructor.

        :param args: Passed to parent class.
        :param div_id: <div id="...">.
        :param prefix: Bootstrap class' prefix.
        :param attributes: Div attributes (e.g. {"data-bs-ride": "carousel", ...}.
        :param fade: Fade between images instead of using a slide transition.
        :param dark: Carousel dark variant.
        :param kwargs: Passed to parent class.
        """
        super().__init__(*args, **kwargs)
        self.div_id = div_id
        self.prefix = prefix
        self.attributes = attributes
        self.fade = fade
        self.dark = dark

    @staticmethod
    def html_visit(writer: HTML5Translator, node: "CarouselMainNode"):
        """Append opening tags to document body list."""
        writer.body.append(
            writer.starttag(
                node,
                "div",
                CLASS=node.classes(
                    node.CLASSES,
                    node.CLASSES_FADE if node.fade else [],
                    node.CLASSES_DARK if node.dark else [],
                ),
                ids=[node.div_id],
                **node.attributes,
            )
        )

    @staticmethod
    def html_depart(writer: HTML5Translator, _):
        """Append closing tags to document body list."""
        writer.body.append("</div>\n")


class SubNode(BaseNode, metaclass=ABCMeta):
    """Base class for child nodes under main node."""

    @property
    def main_node(self) -> CarouselMainNode:
        """Return the main carousel node instance."""
        return self.parent  # noqa

    @property
    def prefix(self) -> str:
        """Return Bootstrap class' prefix."""
        return self.main_node.prefix


class CarouselInnerNode(SubNode):
    """Secondary div that contains the image divs."""

    CLASSES = ["carousel-inner"]

    @staticmethod
    def html_visit(writer: HTML5Translator, node: "CarouselInnerNode"):
        """Append opening tags to document body list."""
        writer.body.append(writer.starttag(node, "div", CLASS=node.classes()))

    @staticmethod
    def html_depart(writer: HTML5Translator, _):
        """Append closing tags to document body list."""
        writer.body.append("</div>\n")


class CarouselItemNode(SubNode):
    """Div that contains an image."""

    CLASSES = ["carousel-item"]
    CLASSES_ACTIVE = ["active"]

    def __init__(self, *args, active: bool = False, **kwargs):
        """Constructor.

        :param args: Passed to parent class.
        :param active: Append active class to div, needed for first image.
        :param kwargs: Passed to parent class.
        """
        super().__init__(*args, **kwargs)
        self.active = active

    @property
    def main_node(self) -> CarouselMainNode:
        """Return the main carousel node instance."""
        return self.parent.parent  # noqa

    @staticmethod
    def html_visit(writer: HTML5Translator, node: "CarouselItemNode"):
        """Append opening tags to document body list."""
        writer.body.append(
            writer.starttag(
                node,
                "div",
                CLASS=node.classes(node.CLASSES, node.CLASSES_ACTIVE if node.active else []),
            )
        )

    @staticmethod
    def html_depart(writer: HTML5Translator, _):
        """Append closing tags to document body list."""
        writer.body.append("</div>\n")


class CarouselControlNode(SubNode):
    """Previous/next buttons."""

    CLASSES_NEXT = ["carousel-control-next"]
    CLASSES_NEXT_ICON = ["carousel-control-next-icon"]
    CLASSES_PREV = ["carousel-control-prev"]
    CLASSES_PREV_ICON = ["carousel-control-prev-icon"]
    CLASSES_TOP = ["my-4", "*scc-top-control"]
    CLASSES_SHADOW = ["*scc-shadow-control"]
    CLASSES_HIDDEN = ["visually-hidden"]

    def __init__(self, *args, prev: bool = False, top: bool = False, shadow: bool = False, **kwargs):
        """Constructor.

        :param args: Passed to parent class.
        :param prev: Previous button if True, else Next button.
        :param top: Display controls at the top of the image instead of the middle.
        :param shadow: Show a shadow around the icons for better visibility when an image is a similar color.
        :param kwargs: Passed to parent class.
        """
        super().__init__(*args, **kwargs)
        self.prev = prev
        self.top = top
        self.shadow = shadow

    @staticmethod
    def html_visit(writer: HTML5Translator, node: "CarouselControlNode"):
        """Append opening tags to document body list."""
        writer.body.append(
            writer.starttag(
                node,
                "button",
                CLASS=node.classes(
                    node.CLASSES_PREV if node.prev else node.CLASSES_NEXT,
                    node.CLASSES_TOP if node.top else [],
                    node.CLASSES_SHADOW if node.shadow else [],
                ),
                type="button",
                **{"data-bs-target": f"#{node.main_node.div_id}", "data-bs-slide": "prev" if node.prev else "next"},
            )
        )

        # Nested icon.
        writer.body.append(
            writer.starttag(
                node,
                "span",
                "",
                CLASS=node.classes(node.CLASSES_PREV_ICON if node.prev else node.CLASSES_NEXT_ICON),
                **{"aria-hidden": "true"},
            )
        )
        writer.body.append("</span>\n")

        # Nested hidden text for screen readers.
        writer.body.append(writer.starttag(node, "span", "", CLASS=node.classes(node.CLASSES_HIDDEN)))
        writer.body.append("Previous" if node.prev else "Next")
        writer.body.append("</span>\n")

    @staticmethod
    def html_depart(writer: HTML5Translator, _):
        """Append closing tags to document body list."""
        writer.body.append("</button>\n")


class CarouselIndicatorsNode(SubNode):
    """Indicators."""

    CLASSES = ["carousel-indicators"]
    CLASSES_ACTIVE = ["active"]
    CLASSES_TOP = ["my-4", "*scc-top-indicator"]
    CLASSES_SHADOW = ["*scc-shadow-indicator"]

    def __init__(self, *args, count: int = 0, top: bool = False, shadow: bool = False, **kwargs):
        """Constructor.

        :param args: Passed to parent class.
        :param count: Number of images.
        :param top: Display indicators at the top of the image instead of the middle.
        :param shadow: Show a shadow around the icons for better visibility when an image is a similar color.
        :param kwargs: Passed to parent class.
        """
        super().__init__(*args, **kwargs)
        self.count = count
        self.top = top
        self.shadow = shadow

    @staticmethod
    def html_visit(writer: HTML5Translator, node: "CarouselIndicatorsNode"):
        """Append opening tags to document body list."""
        writer.body.append(
            writer.starttag(node, "div", CLASS=node.classes(node.CLASSES, node.CLASSES_TOP if node.top else []))
        )

        # Add indicator buttons.
        for i in range(node.count):
            attributes = {
                "data-bs-target": f"#{node.main_node.div_id}",
                "data-bs-slide-to": f"{i}",
                "aria-label": f"Slide {i+1}",
            }
            if i == 0:
                attributes["aria-current"] = "true"
            writer.body.append(
                writer.starttag(
                    node,
                    "button",
                    "",
                    type="button",
                    CLASS=node.classes(
                        node.CLASSES_ACTIVE if i == 0 else [],
                        node.CLASSES_SHADOW if node.shadow else [],
                    ),
                    **attributes,
                )
            )
            writer.body.append("</button>\n")

    @staticmethod
    def html_depart(writer: HTML5Translator, _):
        """Append closing tags to document body list."""
        writer.body.append("</div>\n")


class CarouselCaptionNode(SubNode):
    """Captions."""

    CLASSES = ["carousel-caption"]
    CLASSES_BG_DARK = ["bg-dark"]
    CLASSES_BG_LIGHT = ["bg-light"]
    CLASSES_BELOW = ["d-sm-block", "*scc-below-control"]
    CLASSES_NOT_BELOW = ["d-none", "d-md-block"]

    def __init__(self, *args, title: str = "", description: str = "", below: bool = False, **kwargs):
        """Constructor.

        :param args: Passed to parent class.
        :param title: Caption heading.
        :param description: Caption paragraph.
        :param below: Display caption below image instead of overlayed on top.
        :param kwargs: Passed to parent class.
        """
        super().__init__(*args, **kwargs)
        self.title = title
        self.description = description
        self.below = below

    @property
    def main_node(self) -> CarouselMainNode:
        """Return the main carousel node instance."""
        return self.parent.parent.parent  # noqa

    @staticmethod
    def html_visit(writer: HTML5Translator, node: "CarouselCaptionNode"):
        """Append opening tags to document body list."""
        writer.body.append(
            writer.starttag(
                node,
                "div",
                CLASS=node.classes(
                    node.CLASSES,
                    node.CLASSES_BG_LIGHT if node.below and node.main_node.dark else [],
                    node.CLASSES_BG_DARK if node.below and not node.main_node.dark else [],
                    node.CLASSES_BELOW if node.below else node.CLASSES_NOT_BELOW,
                ),
            )
        )

        if node.title:
            writer.body.append(writer.starttag(node, "h5", ""))
            writer.body.append(node.title)
            writer.body.append("</h5>\n")

        if node.description:
            writer.body.append(writer.starttag(node, "p"))
            writer.body.append(node.description)
            writer.body.append("\n</p>\n")

    @staticmethod
    def html_depart(writer: HTML5Translator, _):
        """Append closing tags to document body list."""
        writer.body.append("</div>\n")
