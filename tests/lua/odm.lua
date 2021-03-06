local tabletools = require("tabletools")
local cjson = require("json")
local odm = require("odm")
local redis = require("rserver")
odm.redis = redis

-- Connect to redis server
redis.connect('fibpalap1d', 6379)
redis.call('select', 15)

local suite = {}

local model_meta = {
    namespace = 'test:simplemodel',
    id_name = 'id',
    id_type = 1,
    indices = {code=true, group=false}
}

local function commit_data (model, data)
    local num, ctx, flat = # data, 0, {}
    for _, sdata in ipairs(data) do
        table.insert(flat, sdata.action or '')
        table.insert(flat, sdata.id or '')
        table.insert(flat, sdata.score or '')
        local odata = sdata.data or {}
        local count = 0
        table.insert(flat, 0)
        ctx = # flat
        for field, value in pairs(odata) do
            table.insert(flat, field)
            table.insert(flat, value)
            count = count + 1
        end
        flat[ctx] = 2 * count
    end
    return model:commit(# data, flat)
end

suite.test_range_selectors = function ()
    assert_true(odm.range_selectors['ge'](3, 2))
    assert_true(odm.range_selectors['ge'](3, 3))
    assert_false(odm.range_selectors['ge'](3, 4))
end

suite.test_commit_simple = function ()
    odm.redis.call('flushdb')
    local model = odm.model(model_meta)
    local ids = commit_data(model, {{action='add', data={code = 'bla'}},
                                    {action='add', data={code = 'foo'}}})
    assert_equal(# ids, 2)
    assert_equal(ids[1][1], 1)
    assert_equal(ids[1][2], 1)
    assert_equal(ids[2][1], 2)
    assert_equal(ids[2][2], 1)
    --
    assert_equal(redis.call('scard', model.idset), 2)
    --
    -- this should contain an error
    local ids = commit_data(model, {{action='add', data={code = 'bla'}},
                                    {action='add', data={code = 'pippo'}}})
    assert_equal(# ids, 2)
    assert_equal('', ids[1][1])
    assert_equal(0, ids[1][2])
    assert_equal(3, ids[2][1])
    assert_equal(1, ids[2][2])
    --
    assert_equal(redis.call('scard', model.idset), 3)
end

suite.test_commit_update_index = function ()
    odm.redis.call('flushdb')
    local model = odm.model(model_meta)
    local ids = commit_data(model, {{action='add', data={code='pluto', group='planet'}}})
    assert_equal(# ids, 1)
    assert_equal(ids[1][1], 1)
    -- Update the instance with a different group
    ids = commit_data(model, {{action='change', id=1, data={code='pluto', group='smallplanet'}}})
    assert_equal(# ids, 1)
    assert_equal(1, ids[1][1])
end


suite.test_query = function ()
    odm.redis.call('flushdb')
    local model = odm.model(model_meta)
    local ids = commit_data(model, {{action='add', data={code = 'bla'}},
                                    {action='add', data={code = 'foo'}},
                                    {action='add', data={code = 'pluto', group='planet'}}})
    local r = model:query('group', model:temp_key(), {'value', ''})
    assert_equal(r, 2)
    r = model:query('group', model:temp_key(), {'value', 'planet'})
    assert_equal(r, 1)
    r = model:query('group', model:temp_key(), {'value', 'xxxxx'})
    assert_equal(r, 0)
end

return suite
