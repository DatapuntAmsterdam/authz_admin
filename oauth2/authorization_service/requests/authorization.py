"""
    oauth2.authorization_service.authorizationrequest
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements the OAuth2 authorization request as defined in
    RFC6749. Specifically, it deals with:

    * `3.1. Authorization Endpoint
       <https://tools.ietf.org/html/rfc6749#section-3.1>`_
    * `4.1.  Authorization Code Grant
       <https://tools.ietf.org/html/rfc6749#section-4.1>`_
    * `4.2.  Implicit Grant
       <https://tools.ietf.org/html/rfc6749#section-4.2>`_
"""
import functools
import urllib

from aiohttp import web, web_exceptions

from oauth2 import clientregistry


def authorization(*supported_flows):
    """ Returns a decorator that can be used to turn a view into one that
    supports an OAuth2 authorization request.

    :param supported_flows: the flows that this view supports (token, code, ..)
    """
    def decorator(f):
        """ Any view function decorated with this decorator will be called with
        an AuthorizationRequest instance as its single argument.
        """
        @functools.wraps(f)
        def wrapper(request):
            request.__class__ = AuthorizationRequest
            request._supported_flows = set(supported_flows)
            return f(request)
        return wrapper
    return decorator


class AuthorizationRequest(web.Request):
    """ Provides request parsing for an authorization request.

    Parmater specific comments can be found at the properties.

    This implementation aims to be compatible with RFC6749 section 3.1:

    * Parameters sent without a value MUST be treated as if they were omitted
        from the request.
    * The authorization server MUST ignore unrecognized request parameters.
    * Request and response parameters MUST NOT be included more than once.

    :todo
        How can we check whether a request parameter was included more than
        once? (point 3 above)


    On error handling, from section 4.1.2.1 and 4.2.2.1:

    * If the request fails due to a missing,
        invalid, or mismatching redirection URI, or if the client identifier is
        missing or invalid, the authorization server SHOULD inform the resource
        owner of the error and MUST NOT automatically redirect the user-agent
        to the invalid redirection URI.
    * All other errors are communicated back to the client using the redirect
        URI.
    """

    # See RFC6749 section 4.1.2.1 and 4.2.2.1
    QUERY_INVALID_REQUEST = urllib.parse.urlencode({
        'error': 'invalid_request',
        'error_description': 'The request is missing a required parameter,'
                             ' includes an invalid parameter value, includes a'
                             ' parameter more than once, or is otherwise'
                             ' malformed.'
    })

    # See RFC6749 section 4.1.2.1 and 4.2.2.1
    QUERY_UNSUPPORTED_RESPONSE_TYPE = urllib.parse.urlencode({
        'error': 'unsupported_response_type',
        'error_description': 'The authorization server does not support'
                             ' obtaining an access token using this method.'
    })

    @property
    def client(self):
        """ Lazy property that returns the OAuth2 Client that made this request.

        From RFC6749 section 4.1.1 and 4.2.1:

            client_id: REQUIRED. The client identifier as described in Section
            2.2.

        :raises aiohttp.web_exceptions.HTTPBadRequest: if the client_id query
            parameter is not present, invalid, or unknown in the client
            registry.

        :todo
            Once we have settled on a format for the client identifier we can
            do more extensive checks.
        """
        try:
            return self._client
        except AttributeError:
            pass
        client_id = self.query.get('client_id')
        client = client_id and clientregistry.get(client_id.encode('ascii'))
        if not client:
            raise web_exceptions.HTTPBadRequest(body='invalid client_id')
        self._client = client
        return client

    @property
    def redirect_uri(self):
        """ Lazy property that returns the redirect_uri for this request.

        From RFC6749 section 4.1.1 and 4.2.1:

            redirect_uri: OPTIONAL if only one redirect endpoint was registered
            for this client, REQUIRED if more. As described in Section 3.1.2.

        :raises aiohttp.web_exceptions.HTTPBadRequest: if the redirect_uri
            parameter is not present, invalid, or mismatching.
        """
        try:
            return self._redirect_uri
        except AttributeError:
            pass
        client_redirects = self.client.redirect_uris
        redirect_uri = self.query.get('redirect_uri')
        if redirect_uri:  # found: check validity
            redirect_uri = redirect_uri in client_redirects and redirect_uri
        else:  # not found, grab the registered URI if only one has been registered
            redirect_uri = len(client_redirects) == 1 and client_redirects[0]
        if not redirect_uri:
            raise web_exceptions.HTTPBadRequest(
                body='invalid redirect_uri'
            )
        if redirect_uri.find('?') == -1:
            redirect_uri += '?'
        self._redirect_uri = redirect_uri
        return redirect_uri

    @property
    def state(self):
        """ Lazy property that returns the state parameter for this request.

        From RFC6749 section 4.1.1 and 4.2.1:

            state: REQUIRED (RECOMMENDED by RFC).  An opaque value used by the
            client to maintain state between the request and callback. The
            authorization server includes this value when redirecting the user-
            agent back to the client.  The parameter SHOULD be used for
            preventing cross-site request forgery as described in Section 10.12.

        :raises aiohttp.web_exceptions.HTTPSeeOther: if the state parameter is
            missing.
        """
        try:
            return self._state
        except AttributeError:
            pass
        state = self.query.get('state')
        if not state:
            raise web_exceptions.HTTPSeeOther(
                self.redirect_uri + self.QUERY_INVALID_REQUEST)
        self._state = state
        return state

    @property
    def response_type(self):
        """ Lazy property that returns the response_type for this request.

        From RFC6749 section 4.1.1 and 4.2.1:

            response_type: REQUIRED. Value MUST be set to "token" for an
            implicit grant, or to "code" for an authorization code grant.

        :raises aiohttp.web_exceptions.HTTPSeeOther:
            If the response_type is missing or not supported.
        """
        try:
            return self._response_type
        except AttributeError:
            pass
        response_type = self.query.get('response_type')
        if not response_type:
            raise web_exceptions.HTTPSeeOther(
                self.redirect_uri + self.QUERY_INVALID_REQUEST)
        if response_type not in self.supported_flows:
            raise web_exceptions.HTTPSeeOther(
                self.redirect_uri + self.QUERY_UNSUPPORTED_RESPONSE_TYPE)
        self._response_type = response_type
        return response_type

    @property
    def scope(self):
        """ Lazy property that returns the scope for this request.

        From RFC6749 section 4.1.1 and 4.2.1:

            scope: OPTIONAL. The scope of the access request as described by
            Section 3.3.
        """
        raise NotImplementedError()

    @property
    def supported_flows(self):
        try:
            return self._supported_flows
        except AttributeError:
            return set()
