from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy

import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:////tmp/sport_results.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('DATABASE_TRACK_MODIFICATIONS', True)
db = SQLAlchemy(app)

class Contestant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return '<Contestant %r>' % self.name

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contestant = db.Column(db.Integer, db.ForeignKey('contestant.id'), nullable=False)
    competition = db.Column(db.String(80), unique=False, nullable=False)
    
    def __repr__(self):
        return '<Result %r>' % self.contestant

class Time(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    result = db.Column(db.Integer, db.ForeignKey('result.id'), nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.String(512), nullable=True)
    start = db.Column(db.Boolean, unique=False, default=False)
    finish = db.Column(db.Boolean, unique=False, default=False)

    def __repr__(self):
        return '<Time %r %r>' % (self.result, self.time)

def _dict_from_row(row):
    dictres = dict(row.__dict__)
    dictres.pop('_sa_instance_state', None)
    return dictres

@app.route('/contestant', methods=['POST'])
def create_contestant():
    info = request.get_json(silent=True)
    
    if not info:
        abort(400)
    if 'name' not in info:
        abort(400)
    
    existing = Contestant.query.filter_by(name = info['name']).first()
    if existing:
        abort(409)
    
    contestant = Contestant(name=info['name'])
    db.session.add(contestant)
    db.session.commit()

    print('Created contestant {} (id {})'.format(contestant.name, contestant.id))
    
    response = _dict_from_row(contestant)
    
    return jsonify(response)

@app.route('/contestant/<int:contestant_id>/<int:result_id>', methods=['GET'])
def competition_result(contestant_id, result_id):
    contestant = Contestant.query.filter_by(id = contestant_id).first()
    if not contestant:
        abort(404)
    result = Result.query.filter_by(id = result_id).first()
    if not result:
        abort(404)
    
    result_info = {
        'competition': result.competition,
        'id': result.id,
        'times': []
    }
    times = Time.query.filter_by(result = result.id).all()

    started = False
    finished = False
    for time in times:
        if time.start:
            started = True
        if time.finish:
            finished = True
        result_info['times'].append(_dict_from_row(time))
        
    if started and not finished:
        result_info['status'] = 'ongoing'
    elif started and finished:
        result_info['status'] = 'completed'
    else:
        result_info['status'] = 'wtf'
    
    return result_info

@app.route('/contestant/<int:contestant_id>', methods=['GET'])
def contestant_info(contestant_id):
    contestant = Contestant.query.filter_by(id = contestant_id).first()
    if not contestant:
        abort(404)
    
    results = Result.query.filter_by(contestant=contestant.id).all()
    response = {
        'contestant': _dict_from_row(contestant),
        'results': []
    }

    for result in results:
        current_result = competition_result(contestant.id, result.id)
        response['results'].append(current_result)
    
    return response


@app.route('/contestant', methods=['GET'])
def list_contestants():
    contestants = Contestant.query.all()

    response = {}
    response['contestants'] = []
    for contestant in contestants:
        response['contestants'].append(contestant_info(contestant.id))

    return response

@app.route('/competition/<int:contestant_id>', methods=['POST'])
def begin_competition(contestant_id):
    info = request.get_json(silent=True)
    if not info:
        abort(400)
    if 'competition' not in info:
        abort(400)

    contestant = Contestant.query.filter_by(id = contestant_id).first()
    if not contestant:
        abort(404)
    
    existing = Result.query.filter_by(contestant=contestant_id).first()
    if existing:
        abort(409)
    
    result = Result(contestant=contestant_id, competition=info['competition'])
    db.session.add(result)
    db.session.commit()
    db.session.flush()

    start_time = Time(result=result.id, description='Start time', start=True)
    db.session.add(start_time)
    db.session.commit()

    print('Begun competition {} for {} with time {}'.format(result.competition, contestant, start_time.time))

    response = {
        'result': _dict_from_row(result),
        'time': _dict_from_row(start_time)
    }
    return jsonify(response)

@app.route('/competition/<int:contestant_id>/<int:result_id>', methods=['PUT'])
def add_time(contestant_id, result_id):
    info = request.get_json(silent=True)
    if not info:
        abort(400)
    if 'description' not in info:
        abort(400)
    
    contestant = Contestant.query.filter_by(id = contestant_id).first()
    if not contestant:
        abort(404)
    result = Result.query.filter_by(id = result_id).first()
    if not result:
        abort(404)

    end = (True if 'finish' in info else False)
    time = Time(result=result.id, description=info['description'], finish=end)
    db.session.add(time)
    db.session.commit()

    if end:
        print("Logged a finish time from {} for result {}: {}".format(contestant, result, time.time))
    else:
        print("Logged an intermediate split time from {} for result {}: {}".format(contestant, result, time.time))

    return jsonify(_dict_from_row(time))


@app.route('/competition/<int:contestant_id>/<int:result_id>', methods=['GET'])
def get_result(contestant_id, result_id):
    contestant = Contestant.query.filter_by(id = contestant_id).first()
    if not contestant:
        abort(404)
    result = Result.query.filter_by(id = result_id).first()
    if not result:
        abort(404)
    
    times = Time.query.filter_by(id = result_id).all()
    response = {
        'contestant': _dict_from_row(contestant),
        'competition': _dict_from_row(result),
        'times': []
    }

    for time in times:
        response['times'].append(_dict_from_row(time))
    
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0")