"""
All kinds of supporting functions for views and models.
"""
import pytz
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage
from django.http import Http404
from .models import (Sr, Subscribed, Flag)
from .utils_search import search_results_buffer


def prepare_paginated_user_list(user_list, page):
    """
    Receives a list and a page number, and returns the appropriate page. If
    the page doesn't exist, it raises Http404.
    """
    PER_PAGE = getattr(settings, 'USERS_PER_PAGE', 20)
    ORPHANS = getattr(settings, 'USERS_ORPHANS', 0)

    paginated = Paginator(user_list, per_page=PER_PAGE,  orphans=ORPHANS)
    try:
        user_page = paginated.page(page)
    except EmptyPage:  # out of range
        raise Http404
    except ValueError:  # not a number
        raise Http404

    return user_page


def get_paginated_user_list(user_list, page, user):
    """
    Return one page of a list of user objects to be handed to the template,
    complete with auth user's geolocation values attached for display of the
    distance between the two users.

    :user_list: User queryset to be paginated.
    :page: the number of the page to return.
    :user: a User instance, usually request.user, from whose geolocation the
           distances to all users the the returned page are calculated.
    """
    user_page = prepare_paginated_user_list(user_list, page)
    user_list = add_auth_user_latlng(user, user_page.object_list)
    user_page.object_list = user_list
    return user_page


def update_list_of_subscribed_subreddits(user, subscribed):
    """
    Get a list of subreddits and update the user account, adding new
    subreddits and removing deleted ones from the user's subscription
    list. Do NOT simply remove all and then add the current list,
    because that would lose the user's "is_favorite" value that is
    part of the Subscribed model.
    """
    for row in subscribed:
        sr, sr_created = Sr.objects.get_or_create(id=row['id'], defaults={
            'name': row['display_name'],  # display_name
            'created': datetime.utcfromtimestamp(
                int(row['created_utc'])).replace(tzinfo=pytz.utc),
            'url': row['url'],
            'over18': row['over18'],
            'lang': row['lang'],
            'title': row['title'],
            'display_name': row['display_name'],
            'subreddit_type': row['subreddit_type'],
            'subscribers': row['subscribers'], })
        # Add the user as subscriber to the subredit object, if that's
        # not already the case.
        sub, sub_created = Subscribed.objects.get_or_create(
            user=user, sr=sr, defaults={
                'user_is_contributor': bool(row['user_is_contributor']),
                'user_is_moderator': bool(row['user_is_moderator']),
                'user_is_subscriber': bool(row['user_is_subscriber']),
                'user_is_banned': bool(row['user_is_banned']),
                'user_is_muted': bool(row['user_is_muted']), })
        # If the user was newly added to the subreddit, count it as
        # a local user for that subreddit. (a user of the sr who is
        # also a user on this site)
        if sub_created:
            sr.subscribers_here += 1
            sr.save()
    # After adding the user to all subs, now check if they are still
    # added to subs they are no longer subbed to.
    sr_ids = [row['id'] for row in subscribed]
    to_del = Subscribed.objects.filter(user=user).exclude(sr__in=sr_ids)
    for row in to_del:
        row.sr.subscribers_here -= 1
        row.sr.save()
        row.delete()


def get_user_list_after(request, view_user, n=5):
    """
    From the search buffer, return a list of "n" user objects after view_user.
    """
    search_results_buffer(request)
    buff = request.session['search_results_buffer']
    try:
        idx = buff.index(view_user.username)
    except ValueError:  # view_user is not part of buffer, begin at index 0
        return get_user_list_from_username_list(buff[:n])

    if (len(buff)-1) <= n:
        # buff minus view_user is n? then use entire list minus view_user
        return get_user_list_from_username_list(buff[:idx] + buff[idx+1:])

    usernames = buff[idx+1:idx+1+n]  # get n users after view_user
    if len(usernames) < n:  # if end-of-list was reached, wrap around
        n2 = n - len(usernames)
        usernames += buff[0:n2]
    return get_user_list_from_username_list(usernames)


def get_user_list_from_username_list(username_list):
    """
    Return a list of user objects with prefetched profiles and subs,
    from a list of usernames. Important: make sure they are in the
    same order as the username_list.
    """
    # Look up complete info on the users on that list.
    li = User.objects.filter(
        username__in=username_list).prefetch_related('profile', 'subs')
    user_list = []
    for x in username_list:
        for y in li:
            if y.username == x:
                user_list.append(y)
                break
    return user_list


def get_prevnext_user(request, view_user):
    """
    Return previous and next users, relative to view user, from the
    search results list of users.
    """
    username_list = request.session['search_results_buffer']
    try:
        idx = [username_list.index(row) for row in username_list
               if view_user.username == row][0]
    except IndexError:
        return None, None
    try:
        # Try one user to the right.
        next_user = username_list[idx+1]
    except IndexError:
        # End of list? Then start over with the first user, NOT of the
        # user list subset, but of the search result user list in the
        # session cache.
        next_user = username_list[0]
    except UnboundLocalError:
        # View user wasn't on the list (no idx)? Return first user.
        next_user = username_list[0]
    try:
        # Try one user to the left.
        prev_user = username_list[idx-1]
    except IndexError:
        # Beginning of list? Start over with the last user.
        prev_user = username_list[-1]
    except UnboundLocalError:
        # View user wasn't on the list (no idx)? Return first user.
        prev_user = view_user
    # Return the user objects of both.
    return (User.objects.get(username__iexact=prev_user),
            User.objects.get(username__iexact=next_user))


def add_auth_user_latlng(user, user_list):
    """Set the user's geolocation on each user list row."""
    for row in user_list:
        row.profile.set_viewer_latlng(user.profile.lat, user.profile.lng)
    return user_list


def count_matches(user):
    """Return the number of matches (mututal likes) of 'user'."""
    return get_matches_user_queryset(user).distinct().count()


def get_matches_user_queryset(user):
    return User.objects.filter(
        flags_sent__receiver=user, flags_sent__flag=Flag.LIKE_FLAG,
        flags_received__sender=user, flags_received__flag=Flag.LIKE_FLAG)


def get_matches_user_list(user):
    """Return a user_list with all mutual likes for 'user'."""
    user_list = list(get_matches_user_queryset(user))
    for x in user_list:
        # set the datetime they matched
        c1 = x.flags_sent.get(receiver=user.pk).created
        c2 = user.flags_sent.get(receiver=x.pk).created
        setattr(x, 'matched', c1 if c1 > c2 else c2)
    user_list.sort(key=lambda row: row.matched, reverse=True)
    return user_list


def get_user_and_related_or_404(username, *args):
    """Like get_user_or_404 but prefetches the givem related items."""
    if isinstance(username, str):
        q = {'username__iexact': username}
    elif isinstance(username, int):
        q = {'pk': username}
    else:
        raise Http404
    try:
        return User.objects.prefetch_related(*args).get(**q)
    except User.DoesNotExist:
        raise Http404


def normalize_sr_names(li):
    """
    Receive a set of randomly cased subreddit names, and return a set of
    appropriately cased subreddit names.
    """
    sr_qs = Sr.objects.none()
    for x in li:
        sr_qs |= Sr.objects.filter(name__iexact=x)

    return sr_qs.values_list('name', flat=True)
