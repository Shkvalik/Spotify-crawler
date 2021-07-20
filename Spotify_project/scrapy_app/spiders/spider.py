import scrapy
from scrapy import Request
import json

class spotifyspider(scrapy.Spider):
    name = "spotify"

    def start_requests(self):
        url_header = 'https://open.spotify.com/get_access_token?reason=transport&productType=web_player'
        yield Request(url=url_header, callback=self.parse_header)

    def parse_header(self, response):
        d =json.loads(response.text)
        token = 'Bearer ' + d['accessToken']

        playlists = ['1qDG2Kr5iKAj4IjlxwJ0cu']
        for id_playlist in playlists:
            playlist_url = 'https://api.spotify.com/v1/playlists/' + id_playlist + '?fields=collaborative%2Cdescription%2Cfollowers(total)%2Cimages%2Cname%2Cowner(display_name%2Cid%2Cimages%2Curi)%2Cpublic%2Ctracks(items(track.type%2Ctrack.duration_ms)%2Ctotal)%2Curi&additional_types=track%2Cepisode&market=UA'
            headers = {'authorization': token}
            yield Request(playlist_url, headers=headers, callback=self.parse_playlist)

    def parse_playlist(self, response, **kwargs):
        d = json.loads(response.text)
        owner_username = d['owner']['display_name']
        id_user = d['owner']['id']
        cb_kwargs = {
            'owner_username': owner_username,
            'owner_user_id': id_user
        }

        followers_url = 'https://spclient.wg.spotify.com/user-profile-view/v3/profile/' + id_user + '?playlist_limit=10&artist_limit=10&market=from_token'
        yield Request(followers_url, headers=response.request.headers, cb_kwargs=cb_kwargs, callback=self.parse_number_of_users)


    def parse_number_of_users(self, response, owner_username=None, owner_user_id=None , **kwargs):
        d = json.loads(response.text)
        owner_user_followers = d['followers_count']

        following_url = 'https://spclient.wg.spotify.com/user-profile-view/v3/profile/' + owner_user_id + '/following?market=from_token'
        cb_kwargs = {
            'owner_username': owner_username,
            'owner_user_id': owner_user_id,
            'owner_user_followers': owner_user_followers,
            'relationship_type': 'following'
        }
        yield Request(following_url, headers=response.request.headers, cb_kwargs=cb_kwargs, callback=self.parse_users)

        follower_url = 'https://spclient.wg.spotify.com/user-profile-view/v3/profile/' + owner_user_id + '/followers?market=from_token'
        cb_kwargs = {
            'owner_username': owner_username,
            'owner_user_id': owner_user_id,

            'owner_user_followers': owner_user_followers,
            'relationship_type': 'follower'
        }
        yield Request(follower_url, headers=response.request.headers, cb_kwargs=cb_kwargs, callback=self.parse_users)

    def parse_users(self, response, owner_username=None, owner_user_id=None, owner_user_followers=None, relationship_type=None):
        d = json.loads(response.text)
        profiles = d['profiles'][0:]
        for p in profiles:
            finite_item={}
            finite_item['owner_user_id'] = owner_user_id
            finite_item['owner_username'] = owner_username
            finite_item['owner_user_followers'] = owner_user_followers
            s = p['uri'].split(':')
            finite_item['related_user_id'] = s[2]
            finite_item['related_user_name'] = p['name']
            finite_item['related_user_type'] = s[1]
            finite_item['relationship_type'] = relationship_type
            yield finite_item
