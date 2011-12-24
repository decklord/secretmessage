define ['api','TastyModel'], (api,TastyModel) ->

    class User extends TastyModel
        @resourceName : 'userprofile'

        @parse : (data) ->
            delete data['password'] if data['password'] isnt undefined
            return data

        save : () ->
            if @isNew()
                super()
            else
                super(method: "patch")

        parse : (data) ->
            return super(User.parse(data))


    return {
        User: User
    }
