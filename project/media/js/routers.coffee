define ['views'], (views) ->

    class Routers extends Backbone.Router
        routes :
            '' : 'home'

        initialize : (options) ->

        home : ->
            loggedOn = false
            $head = $('#head')
            $head.empty()
            $content = $('#homecontent')
            $content.empty()
            if loggedOn
                #$head_right.append()
            else
                loginViewHeader = new views.LoginViewHeader
                loginViewContent = new views.LoginViewContent
                $head.append(loginViewHeader.render().el)
                $content.append(loginViewContent.render().el)
    return {
        Routers : Routers
    }
