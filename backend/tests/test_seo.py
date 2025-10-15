"""
Testy dla SEO features (sitemap, robots, meta tags)
"""
import pytest
from flask import url_for

def test_sitemap_xml_endpoint_exists(client):
    """Test czy /sitemap.xml endpoint istnieje"""
    response = client.get('/sitemap.xml')
    assert response.status_code == 200
    assert response.content_type == 'application/xml; charset=utf-8'

def test_sitemap_contains_main_pages(client):
    """Test czy sitemap zawiera główne strony"""
    response = client.get('/sitemap.xml')
    xml_content = response.data.decode('utf-8')
    
    # Sprawdź czy zawiera kluczowe URLe
    assert '<loc>' in xml_content
    assert '</loc>' in xml_content
    assert 'main.index' in xml_content or '/' in xml_content
    assert 'changefreq' in xml_content
    assert 'priority' in xml_content

def test_sitemap_xml_format(client):
    """Test czy sitemap ma poprawny format XML"""
    response = client.get('/sitemap.xml')
    xml_content = response.data.decode('utf-8')
    
    assert '<?xml version="1.0" encoding="UTF-8"?>' in xml_content
    assert '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' in xml_content
    assert '</urlset>' in xml_content

def test_robots_txt_endpoint_exists(client):
    """Test czy /robots.txt endpoint istnieje"""
    response = client.get('/robots.txt')
    assert response.status_code == 200
    assert response.content_type == 'text/plain; charset=utf-8'

def test_robots_txt_content(client):
    """Test czy robots.txt ma poprawną zawartość"""
    response = client.get('/robots.txt')
    content = response.data.decode('utf-8')
    
    assert 'User-agent: *' in content
    assert 'Allow: /' in content
    assert 'Disallow: /admin/' in content
    assert 'Sitemap:' in content

def test_robots_txt_disallows_sensitive_paths(client):
    """Test czy robots.txt blokuje wrażliwe ścieżki"""
    response = client.get('/robots.txt')
    content = response.data.decode('utf-8')
    
    # Sprawdź czy blokuje kluczowe ścieżki
    assert 'Disallow: /admin/' in content
    assert 'Disallow: /audio/' in content
    assert 'Disallow: /billing/' in content

def test_base_template_has_seo_meta_tags(client):
    """Test czy base template zawiera SEO meta tags"""
    response = client.get('/')
    html = response.data.decode('utf-8')
    
    # Sprawdź czy są meta tagi
    assert '<meta name="description"' in html
    assert '<meta name="keywords"' in html
    assert '<meta name="author"' in html
    assert 'WaveBulk' in html

def test_base_template_has_og_tags(client):
    """Test czy są Open Graph tags"""
    response = client.get('/')
    html = response.data.decode('utf-8')
    
    assert 'property="og:type"' in html
    assert 'property="og:title"' in html
    assert 'property="og:description"' in html

def test_base_template_has_twitter_card(client):
    """Test czy są Twitter Card tags"""
    response = client.get('/')
    html = response.data.decode('utf-8')
    
    assert 'name="twitter:card"' in html
    assert 'name="twitter:title"' in html
    assert 'name="twitter:description"' in html

def test_canonical_url_present(client):
    """Test czy jest canonical URL"""
    response = client.get('/')
    html = response.data.decode('utf-8')
    
    assert '<link rel="canonical"' in html

def test_structured_data_schema_org(client):
    """Test czy jest Schema.org structured data"""
    response = client.get('/')
    html = response.data.decode('utf-8')
    
    assert 'application/ld+json' in html
    assert '@context' in html
    assert 'schema.org' in html
    assert 'SoftwareApplication' in html


