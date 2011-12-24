window.fbAsyncInit = ->
  FB.Event.subscribe 'auth.statusChange', (authResponse) ->
      switch authResponse.status
          when "connected"
              FB.api "/me", (response) ->
                  fbUser = {
                      first_name : response.first_name
                      last_name : response.last_name
                      email : response.email
                      facebook_auth : authResponse.authResponse
                  }
                  console.log(fbUser)
          
  FB.init
    appId      : '25654264113',
    status     : true,
    cookie     : true,
    xfbml      : true,
    oauth      : true,

#init facebook
id = 'facebook-jssdk'
if document.getElementById(id)
    return
js = document.createElement('script')
js.id = id
js.async = true
js.src = "//connect.facebook.net/en_US/all.js"
document.getElementsByTagName('head')[0].appendChild(js)
