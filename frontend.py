"""Defines the web routes of the website.

For actual content generation see the content.py module.
"""
from flask import Blueprint, render_template, jsonify, request, redirect
from flask_nav.elements import Navbar, Link

from .content import get_cluster_plot, search_gene_names, get_mch_scatter, get_mch_box, get_mch_box_two_species,\
    find_orthologs, FailToGraphException
from .nav import nav
from .cache import cache

frontend = Blueprint('frontend', __name__) # Flask "bootstrap"

nav.register_element('frontend_top',
                     Navbar(
                         '',
                         Link('Mouse', './mmu'),
                         Link('Human', './hsa'),))


# Visitor routes
@frontend.route('/')
def index():
    # Index is not needed since this site is embedded as a frame.
    # We use a JavaScript redirection here, since a reverse proxy will be confused about subdirectories.
    return 'To be redirected manually, click <a href="./mmu">here</a>.' + \
           '<script>window.location = "./mmu"; window.location.replace("./mmu");</script>'


@frontend.route('/mmu')
def mouse():
    return render_template('speciesview.html', species='mmu')


@frontend.route('/hsa')
def human():
    return render_template('speciesview.html', species='hsa')


@frontend.route('/standalone/<species>/<gene>')
def standalone(species, gene):  # View gene body mCH plots alone.
    return render_template('mch_standalone.html', species=species, gene=gene)


@frontend.route('/compare/<mmu_gid>/<hsa_gid>')
def compare(mmu_gid, hsa_gid):
    return render_template('compareview.html', mmu_gid=mmu_gid, hsa_gid=hsa_gid)


@frontend.route('/box_combined/<mmu_gid>/<hsa_gid>')
def box_combined(mmu_gid, hsa_gid):
    return render_template(
        'combined_box_standalone.html', mmu_gid=mmu_gid, hsa_gid=hsa_gid)


# API routes
@cache.cached(timeout=3600)
@frontend.route('/plot/cluster/<species>')
def plot_cluster(species):
    try:
        return get_cluster_plot(species)
    except FailToGraphException:
        return 'Failed to produce cluster plot. Contact maintainer.'


@cache.cached(timeout=3600)
@frontend.route('/plot/mch/<species>/<gene>/<level>/<ptile_start>/<ptile_end>')
def plot_mch_scatter(species, gene, level, ptile_start, ptile_end):
    try:
        return get_mch_scatter(species, gene, level,
                               float(ptile_start), float(ptile_end))
    except (FailToGraphException, ValueError) as e:
        print(e)
        return 'Failed to produce mCH levels scatter plot. Contact maintainer.'


@cache.cached(timeout=3600)
@frontend.route('/plot/box/<species>/<gene>/<level>/<outliers_toggle>')
def plot_mch_box(species, gene, level, outliers_toggle):
    if outliers_toggle == 'outliers':
        outliers = True
    else:
        outliers = False

    try:
        return get_mch_box(species, gene, level, outliers)
    except (FailToGraphException, ValueError) as e:
        print(e)
        return 'Failed to produce mCH levels box plot. Contact maintainer.'


@cache.cached(timeout=3600)
@frontend.route(
    '/plot/box_combined/<gene_mmu>/<gene_hsa>/<level>/<outliers_toggle>')
def plot_mch_box_two_species(gene_mmu, gene_hsa, level, outliers_toggle):
    if outliers_toggle == 'outliers':
        outliers = True
    else:
        outliers = False

    try:
        return get_mch_box_two_species(gene_mmu, gene_hsa, level, outliers)
    except (FailToGraphException, ValueError) as e:
        print(e)
        return 'Failed to produce mCH levels box plot. Contact maintainer.'


@cache.cached(timeout=3600)
@frontend.route('/gene/names/<species>')
def search_gene_by_name(species):
    query = request.args.get('q', 'MustHavAQueryString')
    return jsonify(search_gene_names(species, query))


@frontend.route('/gene/orthologs/<species>/<geneID>')
def orthologs(species, geneID):
    geneID = geneID.split('.')[0]
    if species == 'mmu':
        return jsonify(find_orthologs(mmu_gid=geneID))
    else:
        return jsonify(find_orthologs(hsa_gid=geneID))
