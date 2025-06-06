from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db
from .models import Farm, User
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)

def format_gsc(ganancia):
    """
    Convierte ganancia en float (oro decimal) a formato 'XgYsZc'
    Suponiendo: 1 oro = 100 plata, 1 plata = 100 cobre
    """
    total_cobre = int(round(ganancia * 10000))  # oro * 10000 para pasar a cobre
    oro = total_cobre // 10000
    resto = total_cobre % 10000
    plata = resto // 100
    cobre = resto % 100
    return f"{oro}g{plata}s{cobre}c"

def gsc_to_float(g, s, c):
    """Convierte G/S/C enteros a float en oro decimal."""
    total_cobre = g * 10000 + s * 100 + c
    return total_cobre / 10000

@main_bp.route('/')
def index():
    farmeos = Farm.query.all()
    farmeos_formateados = []
    for farm in farmeos:
        farmeos_formateados.append({
            "nombre": farm.nombre,
            "veces_realizadas": farm.veces_realizadas,
            "ganancia_formateada": format_gsc(farm.ganancia)
        })
    return render_template('index.html', farmeos=farmeos_formateados)

@main_bp.route('/admin')
@login_required
def admin_panel():
    if current_user.role != 'admin':
        flash("No tienes permisos para acceder a esta sección.")
        return redirect(url_for('main.index'))
    farmeos = Farm.query.all()
    farmeos_formateados = []
    for farm in farmeos:
        farmeos_formateados.append({
            "id": farm.id,
            "nombre": farm.nombre,
            "veces_realizadas": farm.veces_realizadas,
            "ganancia_formateada": format_gsc(farm.ganancia)
        })
    return render_template('admin_panel.html', farmeos=farmeos_formateados)

@main_bp.route('/admin/add', methods=['GET', 'POST'])
@login_required
def add_farm():
    if current_user.role not in ['admin', 'editor']:
        flash("No tienes permisos para añadir farmeos.")
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        nombre = request.form['nombre']
        veces = int(request.form['veces_realizadas'])
        # Recibir G, S, C por separado
        g = int(request.form.get('gold', 0))
        s = int(request.form.get('silver', 0))
        c = int(request.form.get('copper', 0))
        ganancia = gsc_to_float(g, s, c)

        nuevo_farm = Farm(nombre=nombre, veces_realizadas=veces, ganancia=ganancia)
        db.session.add(nuevo_farm)
        db.session.commit()
        flash("Farmeo agregado correctamente.")
        return redirect(url_for('main.admin_panel'))
    return render_template('add_farm.html')

@main_bp.route('/admin/edit/<int:farm_id>', methods=['GET', 'POST'])
def edit_farm(farm_id):
    farm = Farm.query.get_or_404(farm_id)
    if request.method == 'POST':
        farm.nombre = request.form['nombre']
        farm.veces_realizadas = int(request.form['veces_realizadas'])
        g = int(request.form.get('gold', 0))
        s = int(request.form.get('silver', 0))
        c = int(request.form.get('copper', 0))
        farm.ganancia = gsc_to_float(g, s, c)
        db.session.commit()
        flash("Farmeo actualizado correctamente.")
        return redirect(url_for('main.admin_panel'))

    # Para mostrar los valores en el formulario, extraemos G/S/C de la ganancia float
    total_cobre = int(round(farm.ganancia * 10000))
    farm.gold = total_cobre // 10000
    resto = total_cobre % 10000
    farm.silver = resto // 100
    farm.copper = resto % 100

    return render_template('edit_farm.html', farm=farm)

@main_bp.route('/admin/delete/<int:farm_id>', methods=['POST'])
def delete_farm(farm_id):
    farm = Farm.query.get_or_404(farm_id)
    db.session.delete(farm)
    db.session.commit()
    flash("Farmeo eliminado correctamente.")
    return redirect(url_for('main.admin_panel'))

@main_bp.route('/admin/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    if current_user.role != 'admin':
        flash("No tienes permisos para crear usuarios.")
        return redirect(url_for('main.admin_panel'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role', 'user')
        if User.query.filter_by(username=username).first():
            flash('El usuario ya existe.')
        else:
            user = User(username=username, role=role)
            user.password = password
            db.session.add(user)
            db.session.commit()
            flash('Usuario creado correctamente.')
            return redirect(url_for('main.users_panel'))
    return render_template('create_user.html')

@main_bp.route('/admin/users')
@login_required
def users_panel():
    if current_user.role != 'admin':
        flash("No tienes permisos para ver usuarios.")
        return redirect(url_for('main.admin_panel'))
    users = User.query.all()
    return render_template('users_panel.html', users=users)

@main_bp.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'admin':
        flash("No tienes permisos para editar usuarios.")
        return redirect(url_for('main.admin_panel'))
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        if request.form['password']:
            user.password = request.form['password']
        user.role = request.form.get('role', 'user')
        db.session.commit()
        flash('Usuario actualizado correctamente.')
        return redirect(url_for('main.users_panel'))
    return render_template('edit_user.html', user=user)

@main_bp.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash("No tienes permisos para eliminar usuarios.")
        return redirect(url_for('main.admin_panel'))
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('Usuario eliminado correctamente.')
    return redirect(url_for('main.users_panel'))
