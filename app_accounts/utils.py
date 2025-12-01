# app_accounts/utils.py
def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def parse_user_agent(ua_string: str):
    """
    অতিরিক্ত লাইব্রেরি ছাড়া খুব simple parse.
    চাইলে পরবর্তীতে python-user-agents ব্যবহার করতে পারো।
    """
    ua_string = ua_string or ""

    browser = ""
    if "Chrome" in ua_string and "Safari" in ua_string:
        browser = "Chrome"
    elif "Firefox" in ua_string:
        browser = "Firefox"
    elif "Safari" in ua_string:
        browser = "Safari"
    elif "Edge" in ua_string:
        browser = "Edge"

    os_name = ""
    if "Windows" in ua_string:
        os_name = "Windows"
    elif "Mac OS" in ua_string or "Macintosh" in ua_string:
        os_name = "macOS"
    elif "Android" in ua_string:
        os_name = "Android"
    elif "iPhone" in ua_string or "iPad" in ua_string:
        os_name = "iOS"
    elif "Linux" in ua_string:
        os_name = "Linux"

    device_type = "Desktop"
    if "Mobile" in ua_string or "Android" in ua_string or "iPhone" in ua_string:
        device_type = "Mobile"
    if "iPad" in ua_string or "Tablet" in ua_string:
        device_type = "Tablet"

    return device_type, browser, os_name
