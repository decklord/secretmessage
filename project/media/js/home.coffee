$(document).ready ->
    $('#date').datetimepicker()

    $('.new').click ->
        $('.form').toggle('fast')
        $('.alert').toggle('fast')
        return false

    $('#submit').click ->
        
        #date format: YYYY-MM-DD HH:MM[:ss[.uuuuuu]] 
        dateIsset = $('#date').val()
        if dateIsset != ""
            future = $('#date').datetimepicker('getDate')
            now = new Date()
            ttr = Math.floor((future.getTime() - now.getTime() )/1000)
        else
            ttr = null

        data = {
            description : $('#title').val()
            message : $('#message').val()
            time_to_reveal : ttr
        }

        if data.description != "" && data.message != "" && data.time_to_reveal != ""

            $.ajax
                contentType: "application/json"
                type: "POST"
                data: JSON.stringify(data)
                dataType: "json"
                url : "/api/resources/message/"
                success : (response, status, xhr) ->
                    location = xhr.getResponseHeader( 'Location' )
                    $.ajax
                        contentType: "application/json"
                        type: "GET"
                        url : location
                        success : (r) ->
                            console.log(r)
                            $('.link').html("<a href='message/"+r.code+"/'>Mensaje Oculto!</a>")
                            $('.alert').toggle('fast')
                            $('.form').toggle('fast')
                            $('#date').val("")
                            $('#title').val("")
                            $('#message').val("")


                error : (error) ->
                    console.log "Error :("
                    console.log error
        
        else
            alert("Missing Fields")
