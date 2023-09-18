"""Sphinx directives."""
from typing import List, Optional, Tuple

from docutils.nodes import caption, Element, image as docutils_image, legend, reference
from docutils.parsers.rst.directives import flag, unchanged
from sphinx.util import logging as sphinx_logging
from sphinx.util.docutils import SphinxDirective

from sphinx_carousel import nodes

ImageTuple = Tuple[docutils_image, Optional[reference], str, str]


class Carousel(SphinxDirective):
    """Sphinx directive implementing `.. carousel::` in documents."""

    has_content = True
    option_spec = {
        # Div data attributes.
        "data-bs-interval": unchanged,
        "data-bs-keyboard": unchanged,
        "data-bs-pause": unchanged,
        "data-bs-ride": unchanged,
        "data-bs-wrap": unchanged,
        "data-bs-touch": unchanged,
        # Crossfade/dark.
        "no_fade": flag,
        "show_fade": flag,
        "no_dark": flag,
        "show_dark": flag,
        # Controls/indicators.
        "no_buttons_on_top": flag,
        "show_buttons_on_top": flag,
        "no_controls": flag,
        "show_controls": flag,
        "no_indicators": flag,
        "show_indicators": flag,
        "no_shadows": flag,
        "show_shadows": flag,
        # Captions.
        "no_captions_below": flag,
        "show_captions_below": flag,
    }

    def images(self) -> List[ImageTuple]:
        """Return list of image/figure nodes along with other associated data.

        :return: Image node, parent reference node if :target: was specified, and figure's title/description if available.
        """
        # Create temporary empty document to dump nested image/figure directives into.
        directive_content = Element()
        directive_content.document = self.state.document
        self.state.nested_parse(self.content, self.content_offset, directive_content)

        images = []
        for image in directive_content.traverse(docutils_image):
            # Handle linked images.
            linked_image = image.parent if image.parent.hasattr("refuri") else None
            # Handle captions.
            node = (linked_image or image).next_node(caption, siblings=True, ascend=False, descend=False)
            title = node.astext() if node else ""
            node = (linked_image or image).next_node(legend, siblings=True, ascend=False, descend=False)
            description = node.astext() if node else ""
            # Done with image.
            images.append((image, linked_image, title, description))

        return images

    def config_read_flag(self, name: str) -> bool:
        """Evaluate a directive flag option and the corresponding Sphinx conf.py entry as fallback.

        :param name: Suffix.
        """
        if f"show_{name}" in self.options:
            return True
        if f"no_{name}" in self.options:
            return False
        if self.config[f"carousel_show_{name}"] is True:
            return True
        return False

    def create_inner_node(self, images: List[ImageTuple]) -> Element:
        """Return carousel-inner div node along with child nodes such as images and captions.

        :param images: Output of self.images().
        """
        prefix = self.config["carousel_bootstrap_prefix"]
        captions_below = self.config_read_flag("captions_below")
        items = []

        for idx, (image, linked_image, title, description) in enumerate(images):
            image["classes"] += [f"{prefix}d-block", f"{prefix}w-100"]
            child_nodes = [linked_image or image]
            if title or description:
                child_nodes.append(nodes.CarouselCaptionNode(title=title, description=description, below=captions_below))
            items.append(nodes.CarouselItemNode("", *child_nodes, active=idx == 0))

        return nodes.CarouselInnerNode("", *items)

    def run(self) -> List[Element]:
        """Main method."""
        images = self.images()
        if not images:
            log = sphinx_logging.getLogger(__name__)
            log.warning("No images specified in carousel.", location=(self.env.docname, self.lineno))
            return []

        main_div = nodes.CarouselMainNode(
            div_id=f"carousel-{self.env.new_serialno('carousel')}",
            prefix=self.config["carousel_bootstrap_prefix"],
            attributes={k: v for k, v in self.options.items() if k.startswith("data-")},
            fade=self.config_read_flag("fade"),
            dark=self.config_read_flag("dark"),
        )
        buttons_on_top = self.config_read_flag("buttons_on_top")
        shadows = self.config_read_flag("shadows")

        # Build indicators.
        if self.config_read_flag("indicators"):
            main_div.append(nodes.CarouselIndicatorsNode(count=len(images), top=buttons_on_top, shadow=shadows))

        # Build carousel-inner div.
        main_div.append(self.create_inner_node(images))

        # Build control buttons.
        if self.config_read_flag("controls"):
            main_div.append(nodes.CarouselControlNode(top=buttons_on_top, shadow=shadows, prev=True))
            main_div.append(nodes.CarouselControlNode(top=buttons_on_top, shadow=shadows))

        return [main_div]
