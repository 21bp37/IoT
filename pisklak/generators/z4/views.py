from flask import Blueprint, request, render_template

mod = Blueprint('self_update', __name__)

clients: list[dict] = []


@mod.route('/generators', methods=['GET', 'POST'])
def generators():
    if request.method == 'POST':
        sid = request.form['id']
        gen = list(filter(lambda client: client['id'] == sid, clients))[0]
        gen['protocol'] = request.form['protocol']
        gen['interval'] = request.form['interval']
        gen['data_source'] = request.form['source']
        gen['url'] = request.form['url']
        return render_template('manager.html', client=gen)
    if request.method == 'GET' and request.args.get('id') is not None:
        try:
            selected = list(filter(lambda client: client['id'] == request.args.get('id'), clients))
            return render_template('manager.html', client=selected[0])
        except IndexError:
            return 'generator not found.'
    return render_template('generators.html', clients=clients)
