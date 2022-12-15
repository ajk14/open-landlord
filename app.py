from flask import Flask, render_template, flash, request, redirect, send_from_directory, jsonify
from flask_marshmallow import Marshmallow
from flask_cors import CORS, cross_origin
from marshmallow import fields
from models import db, Landlord, Property, Alias
from constants import SEARCH_DEFAULT_MAX_RESULTS
import os
import utils
import constants


app = Flask(__name__,static_folder='frontend/build',static_url_path='')
ma = Marshmallow(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['LANDLORD_DATABASE_URI']
db.init_app(app)
CORS(app)


# Schema API initializations 
class LandlordSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Landlord
        include_fk = True
        include_relationships = True
        load_instance = True

    name = ma.auto_field()
    id = ma.auto_field()
    address = ma.auto_field()
    property_count = ma.auto_field()
    eviction_count = ma.auto_field()
    eviction_count_per_property = fields.Float(dump_only=True)
    code_violations_count = ma.auto_field()
    code_violations_count_per_property = fields.Float(dump_only=True)
    police_incidents_count = ma.auto_field()
    police_incidents_count_per_property = fields.Float(dump_only=True)
    tenant_complaints_count = ma.auto_field()
    tenant_complaints_count_per_property = fields.Float(dump_only=True)


class PropertySchema(ma.Schema):
    class Meta:
        fields = (
            "parcel_id", 
            "address", 
            "latitude", 
            "longitude",
            "id",
            "property_type",
            "owner_id",
            "tenant_complaints",
            "owner_occupied",
            "unsafe_unfit_count",
            "police_incidents_count",
            "current_use",
            "business_entity_type",
            "longitude",
            "code_violations_count",
            "owner_occupied",
            "business_entity_type",
        )


class AliasSchema(ma.Schema):
    class Meta:
        fields = ("name", "landlord_id")


LANDLORD_SCHEMA = LandlordSchema()
LANDLORDS_SCHEMA = LandlordSchema(many=True)
ALIAS_SCHEMA = AliasSchema()
ALIASES_SCHEMA = AliasSchema(many=True)
PROPERTY_SCHEMA = PropertySchema()
PROPERTIES_SCHEMA = PropertySchema(many=True)


@app.route('/')
def serve():
    return app.send_static_file('index.html')



@app.route('/results')
def search_results(search):
    results = utils.perform_search(search.data['search'])
    return render_template('index.html', results=results, form=search, autocomplete_prompts=utils.get_autocomplete_prompts())


@app.route('/landlord/<id>')
def landlord(id):
    properties_list = utils.get_all_properties_dict(id)
    aliases = utils.get_all_aliases(id)
    landlord = utils.get_enriched_landlord(id, properties_list)
    city_average_stats = utils.get_city_average_stats()
    landlord_stats = utils.get_landlord_stats(id, properties_list, city_average_stats)
    landlord_score = utils.calculate_landlord_score(landlord_stats)
    unsafe_unfit_list = utils.get_unsafe_unfit_properties(id)

    return render_template('landlord.html', landlord=landlord, properties=properties_list, landlord_stats=landlord_stats, 
        city_average_stats=city_average_stats, landlord_score=landlord_score, aliases=aliases, unsafe_unfit_list=unsafe_unfit_list)


@app.route('/property/<id>')
def property(id):
    property = Property.query.filter_by(id=id).first()
    landlord = Landlord.query.filter_by(id=property.owner_id).first()
    return render_template('property.html', property=property.as_dict(), landlord=landlord.as_dict())


@app.route('/faq/')
def faq():
    return render_template('faq.html')

@app.route('/action/')
def action():
    return render_template('action.html')


@app.route('/about/')
def about():
    return render_template('about.html')


@app.errorhandler(404)
def not_found(e):
    return app.send_static_file('index.html')


# API Definitions


@app.route('/api/landlords/top/', methods=['GET'])
@cross_origin()
def get_top_landlords():
    pageSize = int(request.args.get('pageSize')) if request.args.get('pageSize') else constants.DEFAULT_PAGE_SIZE
    pageNumber = int(request.args.get('pageNumber')) if request.args.get('pageNumber') else constants.DEFAULT_PAGE_NUMBER
    sortBy = request.args.get('sortBy').lower() if request.args.get('sortBy') else constants.DEFAULT_SORT_BY
    sortDirection = request.args.get('sortDirection') if request.args.get('sortDirection') else constants.DEFAULT_SORT_DIRECTION

    landlords_paginated = utils.get_ranked_landlords(sortBy, sortDirection, pageNumber, pageSize)

    return jsonify({"total_results": landlords_paginated.total, "landlords": landlords_paginated.items})


@app.route('/api/landlords/<id>', methods=['GET'])
@cross_origin()
def get_landlord(id):
    return LANDLORD_SCHEMA.jsonify(Landlord.query.get(id))


@app.route('/api/landlords/', methods=['POST'])
@cross_origin()
def get_landlords_bulk():
    response_json = request.get_json()
    landlord_ids = response_json["ids"] if "ids" in response_json else []
    landlords = Landlord.query.filter(Landlord.id.in_(landlord_ids)).all()
    landlord_map = {}
    for landlord in landlords:
        landlord_map[landlord.id] = landlord.as_dict()

    return jsonify(landlord_map)


@app.route('/api/landlords/<landlord_id>/aliases', methods=['GET'])
@cross_origin()
def get_landlord_aliases(landlord_id):
    aliases = Alias.query.filter_by(landlord_id=landlord_id).all()
    return ALIASES_SCHEMA.jsonify(aliases)


@app.route('/api/landlords/<landlord_id>/grades', methods=['GET'])
@cross_origin()
def get_landlord_grades(landlord_id):
    landlord = Landlord.query.get(landlord_id).as_dict()
    stats = utils.get_city_average_stats()
    grades = utils.add_grade_and_color(landlord, stats)
    grades.update(utils.calculate_landlord_score(grades))
    return jsonify(grades)


@app.route('/api/landlords/<landlord_id>/properties', methods=['GET'])
@cross_origin()
def get_landlord_properties(landlord_id):
    properties = Property.query.filter_by(owner_id=landlord_id).all()
    return PROPERTIES_SCHEMA.jsonify(properties)


@app.route('/api/landlords/<landlord_id>/unsafe_unfit', methods=['GET'])
@cross_origin()
def get_landlord_unsafe_unfit_properties(landlord_id):
    properties = Property.query.filter(Property.owner_id == landlord_id).filter(Property.unsafe_unfit_count > 0).all()
    return PROPERTIES_SCHEMA.jsonify(properties)


@app.route('/api/stats', methods=['GET'])
@cross_origin()
def get_city_stats():
    stats = utils.get_city_average_stats()
    return stats


@app.route('/api/search', methods=['GET'])
@cross_origin()
def get_search_results():
    max_results = request.args.get('max_results') if request.args.get('max_results') else SEARCH_DEFAULT_MAX_RESULTS
    search_string = request.args.get('query') if request.args.get('query') else ""
    return PROPERTIES_SCHEMA.jsonify(utils.perform_search(search_string, max_results).all())
    

@app.route('/api/properties/<id>', methods=['GET'])
@cross_origin()
def get_property(id):
    return PROPERTY_SCHEMA.jsonify(Property.query.get(id))


if __name__ == '__main__':
    app.run(host='0.0.0.0')