$(document).ready ->
    $('#date').datetimepicker()

    $('#submit').click ->
        #date format: YYYY-MM-DD HH:MM[:ss[.uuuuuu]] 
        future = $('#date').datetimepicker('getDate')
        now = new Date()
        ttr = Math.floor((future.getTime() - now.getTime() )/1000)

        data = {
            description : $('#title').val()
            message : $('#message').val()
            time_to_reveal : ttr
        }

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

            error : (error) ->
                console.log "Error :("
                console.log error
