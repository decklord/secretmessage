require ['models', 'rpc'], (models, rpc) ->

    $(->
	    $('#reg_dialog').dialog
		    autoOpen: false
		    width: 450
		    modal: true
		    resizable: false
		    buttons:
			    "Sign in": ->
                    #Sign Up behaviour
                    if $('#regName').val() == ''
                        return
                    if $('#regLastName').val() == ''
                        return
                    if $('#regEmail').val() == ''
                        return
                    if $('#regPass').val() == ''
                        return
                    if $('#regPass').val().length < 8
                        return
                    if $('#regPass').val() != $('#regPass2').val()
                        return
                    newUser = new models.User
                        first_name : $('#regName').val()
                        last_name : $('#regLastName').val()
                        email : $('#regEmail').val()
                        password : $('#regPass').val()
            
                    $('input').each ->
                        $(@).val('')
                    newUser.save()
                    $(@).dialog("close")
                "Cancel": ->
                    $(@).dialog("close")

	    $('#homeSingUp').click ->
            $('#reg_dialog').dialog('open')
        $('#loginform').validationEngine('attach')
        $('#registerform').validationEngine('attach')
    )

    #Sign in behaviour
    login =  ->
       if $('#email').val() != '' and $('#pass').val() != ''
        credentials =
            email : $('#email').val()
            password : $('#pass').val()
        rpc.execute "authenticate", credentials,
            success : ->
                console.log('You\'re logged in')

            error : ->
                console.log('Error in login')
    $('#btnLogin').click ->
        login()
    $('#pass').keypress (e) ->
        if e.keyCode == '13'
            login()

