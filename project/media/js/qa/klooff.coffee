require ['rpc'], (rpc) ->
    test "Load kloof test module", ->
        ok(true)

    test "Require sync", ->
        ok(rpc isnt undefined)
   
    asyncTest "RPC echo object", ->
        expect(1)

        testMessage = {
            uno : "one"
            dos : 2
            tres : ['three','trois', 'tres']
            cuatro : {
                'cinco' : 'cinco'
            }
        }
        rpc.execute "echo", testMessage,
            success : (response) ->
                deepEqual(testMessage, response)
                start()
            error : (response) ->
                start()

    asyncTest "RPC echo string", ->
        expect(1)

        testMessage = "This is a very unlikely string"
        rpc.execute "echo", testMessage,
            success : (response) ->
                equal(testMessage, response)
                start()
            error : (response) ->
                start()

