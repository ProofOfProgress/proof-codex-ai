from shorts_bot.invideo.fetch_url import normalize_download_url


def test_gdrive_view_link():
    url = "https://drive.google.com/file/d/abc123XYZ/view?usp=sharing"
    out = normalize_download_url(url)
    assert "uc?export=download" in out
    assert "id=abc123XYZ" in out


def test_dropbox_link():
    url = "https://www.dropbox.com/s/xyz/video.mp4?dl=0"
    out = normalize_download_url(url)
    assert "dl=1" in out


def test_direct_url_unchanged():
    url = "https://cdn.example.com/final_short.mp4"
    assert normalize_download_url(url) == url
