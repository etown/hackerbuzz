var express = require('express');
var router = express.Router();
var pgp = require('pg-promise')(/*options*/);

var cn = {
  'database': 'postgres',
  'user': 'postgres',
  'password': process.env.DBPASSWORD,
  'host': process.env.DBHOST,
  'port': 5432
};

var db = pgp(cn); 
router.get('/api/trends', function(req, res, next) {
  var queries=req.query.q.split(',');
  var i;
  var self=this;
  var promises=[];
  for (i = 0; i < queries.length; i++) {
    promises.push(db.query("select distinct(to_char(created_at, 'YYYY-MM-DD')) as date,sum(points) over(order by created_at) as value from items where to_tsvector ('simple', title) @@ to_tsquery ($1) order by date", queries[i]));
  }
  db.tx(function () {
    return this.batch(promises);
  }).then(function (values) {
      res.send(values);
    }, function (reason) {
        console.log(reason);
    });
});

router.get('/api/stories', function(req, res, next) {
  var i;
  var self=this;
  var promises=[];
  promises.push(db.query("select * from items where to_tsvector ('simple', title) @@ to_tsquery ($1) order by id desc", req.query.q));
  db.tx(function () {
    return this.batch(promises);
  }).then(function (values) {
      res.send(values);
    }, function (reason) {
        console.log(reason);
    });
});

router.get('/api/rendered_stories', function(req, res, next) {
  var i;
  var self=this;
  var promises=[];
  promises.push(db.query("select * from items where to_tsvector ('simple', title) @@ to_tsquery ($1) order by id desc", req.query.q));
  db.tx(function () {
    return this.batch(promises);
  }).then(function (values) {
      res.render('stories', {stories: values[0]});
    }, function (reason) {
        console.log(reason);
    });
});


module.exports = router;
