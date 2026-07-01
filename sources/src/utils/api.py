from __future__ import annotations

from datetime import datetime

import requests
from config import API_URL


class LastFmException(Exception):
    def __init__(self, message: str, error_code: int) -> None:
        super().__init__(message, error_code)
        self.message = message
        self.error_code = error_code


class LastFmApi:
    def __init__(self, api_key: str, url: str = API_URL, raw: bool = False) -> None:
        self.api_key = api_key
        self.url = url
        self.raw = raw

    def _call_method(self, method_name: str, data: dict[str, object]) -> dict:
        """Call a Last.fm API method and return the decoded JSON response.

        Args:
            method_name: Last.fm API method name (e.g. 'User.GetRecentTracks').
            data: Request parameters for the method.

        Returns:
            Decoded JSON response as a dict.

        Raises:
            LastFmException: When the API returns an error field.
        """
        data.update(
            {
                "method": method_name,
                "format": "json",
                "api_key": self.api_key,
            }
        )
        response = requests.get(url=self.url, params=data)
        result = response.json()
        if "error" in result:
            raise LastFmException(message=result["message"], error_code=result["error"])
        return result

    @staticmethod
    def _get_image(image_data: list[dict] | None = None, size: str = "medium") -> str:
        """Extract image URL of the given size from Last.fm image data.

        Args:
            image_data: List of image dicts from the API response.
            size: Desired image size key (e.g. 'small', 'medium', 'large').

        Returns:
            URL string for the requested image size.
        """
        assert image_data is not None, "image_data should not be None"
        return next((img["#text"] for img in image_data if img["size"] == size), "")


class User(LastFmApi):
    def __init__(
        self,
        api_key: str,
        url: str = API_URL,
        raw: bool = False,
        username: str | None = None,
    ) -> None:
        super().__init__(api_key, url, raw)
        assert username is not None, "User is not defined"
        self.username = username

    def user_get_recent_tracks(
        self,
        limit: int = 1,
        page: int = 1,
        extended: int = 0,
        current: bool = False,
        from_time: int | None = None,
        to_time: int | None = None,
        raw: bool | None = None,
    ) -> dict:
        """Fetch recently scrobbled tracks for the user (User.GetRecentTracks).

        Args:
            limit: Number of tracks to return.
            page: Result page number.
            extended: Set to 1 to get extended track info (includes artist image/url).
            current: If True, strip the currently-playing track from results.
            from_time: Return tracks after this UNIX timestamp.
            to_time: Return tracks before this UNIX timestamp.
            raw: Override instance-level raw flag for this call.

        Returns:
            Dict with 'attributes' and 'recent_tracks' keys, or raw API response.
        """
        data: dict[str, object] = {
            "user": self.username,
            "limit": limit,
            "page": page,
            "extended": extended,
        }
        if to_time:
            data["to"] = to_time
        if from_time:
            data["from"] = from_time

        recent_tracks = self._call_method("User.GetRecentTracks", data)
        if self.raw or raw:
            return recent_tracks

        result_tracks: dict[str, object] = {
            "attributes": recent_tracks["recenttracks"]["@attr"],
            "recent_tracks": [],
        }
        tracks = recent_tracks["recenttracks"]["track"]
        if isinstance(tracks, dict):
            tracks = [tracks]
        for track in tracks:
            _track: dict[str, object] = {
                "track_name": track["name"].title(),
                "album_name": track["album"]["#text"].title(),
                "album_image": self._get_image(track["image"]),
                "track_url": track["url"],
            }
            if track.get("@attr", {}).get("nowplaying"):
                _track["now_playing"] = track["@attr"]["nowplaying"] == "true"
            if extended:
                _track["artist_image"] = self._get_image(track["artist"]["image"])
                _track["artist_url"] = track["artist"]["url"]
                _track["artist_name"] = track["artist"]["name"].title()
            else:
                _track["artist_name"] = track["artist"]["#text"].title()
            result_tracks["recent_tracks"].append(_track)  # type: ignore[union-attr]

        if current:
            tracks_list = result_tracks["recent_tracks"]
            result_tracks["recent_tracks"] = tracks_list[: len(tracks_list) - 1]  # type: ignore[index]

        return result_tracks

    def user_get_info(self, raw: bool = False) -> dict:
        """Fetch profile info for the user (User.GetInfo).

        Args:
            raw: If True, return the raw API response.

        Returns:
            Dict with 'attributes' and 'user_info' keys, or raw API response.
        """
        data: dict[str, object] = {"user": self.username}
        result = self._call_method("User.GetInfo", data)

        if self.raw or raw:
            return result

        user_info: dict[str, object] = {
            "attributes": result["user"]["@attr"],
            "user_info": {},
        }
        if "user" in result:
            u = result["user"]
            user_info["user_info"].update(u)  # type: ignore[union-attr]
            user_info["user_info"]["image"] = self._get_image(u["image"])  # type: ignore[index]
            user_info["user_info"]["registered"] = (  # type: ignore[index]
                datetime.fromtimestamp(int(u["registered"]["unixtime"])).strftime(
                    "%d-%m-%Y %H:%M:%S"
                )
            )
        return user_info

    def user_get_artist_tracks(
        self,
        raw: bool = False,
        artist: str | None = None,
        from_time: int | None = None,
        to_time: int | None = None,
        page: int = 1,
    ) -> dict:
        """Fetch scrobbled tracks by a specific artist (User.GetArtistTracks).

        Args:
            raw: If True, return the raw API response.
            artist: Artist name to filter by.
            from_time: Return tracks after this UNIX timestamp.
            to_time: Return tracks before this UNIX timestamp.
            page: Result page number.

        Returns:
            Raw API response dict.
        """
        assert artist is not None, "Artist name is not defined"
        data: dict[str, object] = {
            "user": self.username,
            "artist": artist,
            "page": page,
        }
        if from_time:
            data["startTimestamp"] = from_time
        if to_time:
            data["endTimestamp"] = to_time

        return self._call_method("User.GetArtistTracks", data)
