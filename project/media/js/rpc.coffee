define ->
    class Rpc
        constructor : ->
            @rpcUrl = "/api/rpc/"

        execute : (method, params, callbacks) ->
            data = {
                jsonrpc: "2.0"
                method: method
                params : params
                id : Math.random()
            }
            data = JSON.stringify(data)

            $.ajax
                url : @rpcUrl
                data : data
                contentType: "application/json"
                type: "POST"
                dataType: "json"
                success : (r)-> callbacks.success(r.result)
                error : (r)-> callbacks.error(r.error)

    return new Rpc()

