from app.extractor import extract_page_data


def test_extract_product_jsonld():
    html = '''
    <html><head>
      <title>Produto X</title>
      <meta property="og:image" content="https://cdn.example/x.jpg">
      <script type="application/ld+json">
      {"@context":"https://schema.org","@type":"Product","name":"Produto X","image":"https://cdn.example/x.jpg","offers":{"@type":"Offer","price":"99.90","priceCurrency":"BRL"}}
      </script>
    </head><body></body></html>
    '''
    data = extract_page_data(html, "https://example.com/produto")
    assert data["product"]["name"] == "Produto X"
    assert data["product"]["price"] == "99.90"
    assert data["product"]["currency"] == "BRL"
