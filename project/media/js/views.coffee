define [], ->

    class LoginViewHeader extends

        initialize : ->
            _.bindAll(@, 'render')
            @template = _.template($('#header_login_template').html())

        render : ->
            renderedContent = @template(@model.toJSON())
            $(@el).html(renderedContent)
            return @

    class LoginViewContent extends

        initialize : ->
            _bindAll(@, 'render')
            @model.bind('change', @render)
            @template = _.template($('#content_login_template').html())
        render : ->
            renderedContent = @template(@model.toJSON())
            $(@el).html(renderedContent)
            return @


    return {
        LoginViewHeader : LoginViewHeader
        LoginViewContent : LoginViewContent
    }
