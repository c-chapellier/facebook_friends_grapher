
# get username or id from the profile link
def profile_url_to_username_or_id(profile_url):
    if 'profile.php?id=' in profile_url:
        return profile_url.split('profile.php?id=')[1]
    return profile_url.split('facebook.com/')[1]
