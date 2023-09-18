"""A Sphinx extension for creating slideshows using Bootstrap Carousels.

https://sphinx-carousel.readthedocs.io
https://github.com/Robpol86/sphinx-carousel
https://pypi.org/project/sphinx-carousel
"""
from pathlib import Path
from typing import Dict

from docutils.nodes import document
from sphinx.application import Sphinx
from sphinx.util.fileutil import copy_asset_file

from sphinx_carousel import __version__, nodes
from sphinx_carousel.directives import Carousel

CONF_DEFAULT_BOOTSTRAP_ADD_CSS_JS = True
CONF_DEFAULT_BOOTSTRAP_PREFIX = "scbs-"
CONF_DEFAULT_SHOW_BUTTONS_ON_TOP = False
CONF_DEFAULT_SHOW_CAPTIONS_BELOW = False
CONF_DEFAULT_SHOW_CONTROLS = False
CONF_DEFAULT_SHOW_DARK = False
CONF_DEFAULT_SHOW_FADE = False
CONF_DEFAULT_SHOW_INDICATORS = False
CONF_DEFAULT_SHOW_SHADOWS = False


def copy_static(app: Sphinx):
    """Install CSS and JS files into the output directory.

    :param app: Sphinx application object.
    """
    if app.builder.format != "html":
        return

    static_in = Path(__file__).parent / "_static"
    static_out = Path(app.builder.outdir) / "_static"
    static_out.mkdir(exist_ok=True)

    if app.config.carousel_bootstrap_add_css_js:
        copy_asset_file(str(static_in / "bootstrap-carousel.min.css"), str(static_out))
        copy_asset_file(str(static_in / "bootstrap-carousel.min.js"), str(static_out))

    context = {
        "bootstrap_prefix": app.config["carousel_bootstrap_prefix"],
    }
    copy_asset_file(str(static_in / "carousel-custom.css_t"), str(static_out), context)


def include_static_on_demand(app: Sphinx, _: str, __: str, ___: dict, doctree: document):
    """Add CSS and JS files to <head /> only on specific pages that use the directive.

    :param app: Sphinx application object.
    :param _: Unused.
    :param __: Unused.
    :param ___: Unused.
    :param doctree: Tree of docutils nodes.
    """
    if not doctree or not doctree.traverse(nodes.CarouselMainNode):
        return

    if app.config.carousel_bootstrap_add_css_js:
        app.add_css_file("bootstrap-carousel.min.css")
        app.add_js_file("bootstrap-carousel.min.js")

    app.add_css_file("carousel-custom.css")


def setup(app: Sphinx) -> Dict[str, str]:
    """Called by Sphinx during phase 0 (initialization).

    :param app: Sphinx application object.

    :returns: Extension version.
    """
    app.add_config_value("carousel_bootstrap_add_css_js", CONF_DEFAULT_BOOTSTRAP_ADD_CSS_JS, "html")
    app.add_config_value("carousel_bootstrap_prefix", CONF_DEFAULT_BOOTSTRAP_PREFIX, "html")
    app.add_config_value("carousel_show_buttons_on_top", CONF_DEFAULT_SHOW_BUTTONS_ON_TOP, "html")
    app.add_config_value("carousel_show_captions_below", CONF_DEFAULT_SHOW_CAPTIONS_BELOW, "html")
    app.add_config_value("carousel_show_controls", CONF_DEFAULT_SHOW_CONTROLS, "html")
    app.add_config_value("carousel_show_dark", CONF_DEFAULT_SHOW_DARK, "html")
    app.add_config_value("carousel_show_fade", CONF_DEFAULT_SHOW_FADE, "html")
    app.add_config_value("carousel_show_indicators", CONF_DEFAULT_SHOW_INDICATORS, "html")
    app.add_config_value("carousel_show_shadows", CONF_DEFAULT_SHOW_SHADOWS, "html")
    app.add_directive("carousel", Carousel)
    app.connect("builder-inited", copy_static)
    app.connect("html-page-context", include_static_on_demand)
    nodes.CarouselCaptionNode.add_node(app)
    nodes.CarouselControlNode.add_node(app)
    nodes.CarouselIndicatorsNode.add_node(app)
    nodes.CarouselInnerNode.add_node(app)
    nodes.CarouselItemNode.add_node(app)
    nodes.CarouselMainNode.add_node(app)
    return dict(version=__version__)
