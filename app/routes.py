from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response
from . import db
from .models import Farm, User
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash
import re

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
    # Filtros para la vista pública
    query = Farm.query
    filtro_nombre = request.args.get('nombre', '').strip()
    if filtro_nombre:
        query = query.filter(Farm.nombre.ilike(f"%{filtro_nombre}%"))
    filtro_veces = request.args.get('veces_realizadas', '').strip()
    if filtro_veces:
        try:
            filtro_veces = int(filtro_veces)
            query = query.filter(Farm.veces_realizadas == filtro_veces)
        except ValueError:
            pass
    ganancia_min = request.args.get('ganancia_min', '').strip()
    if ganancia_min:
        try:
            ganancia_min = float(ganancia_min)
            query = query.filter(Farm.ganancia >= ganancia_min)
        except ValueError:
            pass
    ganancia_max = request.args.get('ganancia_max', '').strip()
    if ganancia_max:
        try:
            ganancia_max = float(ganancia_max)
            query = query.filter(Farm.ganancia <= ganancia_max)
        except ValueError:
            pass
    filtro_waypoint = request.args.get('waypoint', '').strip()
    if filtro_waypoint:
        query = query.filter(Farm.waypoint.ilike(f"%{filtro_waypoint}%"))
    filtro_duracion = request.args.get('duracion', '').strip()
    if filtro_duracion:
        query = query.filter(Farm.duracion == filtro_duracion)
    filtro_requerimientos = request.args.get('requerimientos', '').strip()
    if filtro_requerimientos:
        query = query.filter(Farm.requerimientos.ilike(f"%{filtro_requerimientos}%"))
    profit_hr_min = request.args.get('profit_hr_min', '').strip()
    if profit_hr_min:
        try:
            profit_hr_min = float(profit_hr_min)
            query = query.filter(Farm.profit_hr >= profit_hr_min)
        except ValueError:
            pass
    profit_hr_max = request.args.get('profit_hr_max', '').strip()
    if profit_hr_max:
        try:
            profit_hr_max = float(profit_hr_max)
            query = query.filter(Farm.profit_hr <= profit_hr_max)
        except ValueError:
            pass
    filtro_limitation = request.args.get('limitation', '').strip()
    if filtro_limitation:
        query = query.filter(Farm.limitation.ilike(f"%{filtro_limitation}%"))
    sort = request.args.get('sort', '')
    sort_map = {
        'nombre': Farm.nombre,
        'veces_realizadas': Farm.veces_realizadas,
        'ganancia': Farm.ganancia,
        'waypoint': Farm.waypoint,
        'duracion': Farm.duracion,
        'requerimientos': Farm.requerimientos,
        'profit_hr': Farm.profit_hr,
        'limitation': Farm.limitation
    }
    if sort:
        for key in sort_map:
            if sort.startswith(key):
                direction = sort.split('_')[1] if '_' in sort else 'asc'
                if direction == 'desc':
                    query = query.order_by(sort_map[key].desc())
                else:
                    query = query.order_by(sort_map[key].asc())
                break
    farmeos = query.all()
    farmeos_formateados = []
    total_farmeos = len(farmeos)
    suma_ganancias = sum(f.ganancia for f in farmeos)
    for farm in farmeos:
        farmeos_formateados.append({
            "nombre": farm.nombre,
            "veces_realizadas": farm.veces_realizadas,
            "ganancia_formateada": format_gsc(farm.ganancia),
            "waypoint": farm.waypoint,
            "duracion": farm.duracion,
            "requerimientos": farm.requerimientos,
            "profit_hr_formateado": format_gsc(farm.profit_hr) if farm.profit_hr is not None else '-',
            "limitation": farm.limitation
        })
    return render_template('index.html', farmeos=farmeos_formateados, total_farmeos=total_farmeos, suma_ganancias=suma_ganancias)

@main_bp.route('/admin')
@login_required
def admin_panel():
    if current_user.role != 'admin':
        flash("No tienes permisos para acceder a esta sección.")
        return redirect(url_for('main.index'))
    # Filtros
    query = Farm.query
    filtro_nombre = request.args.get('nombre', '').strip()
    if filtro_nombre:
        query = query.filter(Farm.nombre.ilike(f"%{filtro_nombre}%"))
    filtro_duracion = request.args.get('duracion', '').strip()
    if filtro_duracion:
        query = query.filter(Farm.duracion == filtro_duracion)
    ganancia_min = request.args.get('ganancia_min', '').strip()
    if ganancia_min:
        try:
            ganancia_min = float(ganancia_min)
            query = query.filter(Farm.ganancia >= ganancia_min)
        except ValueError:
            pass
    ganancia_max = request.args.get('ganancia_max', '').strip()
    if ganancia_max:
        try:
            ganancia_max = float(ganancia_max)
            query = query.filter(Farm.ganancia <= ganancia_max)
        except ValueError:
            pass
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = query.order_by(Farm.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    farmeos = pagination.items
    farmeos_formateados = []
    for farm in farmeos:
        farmeos_formateados.append({
            "id": farm.id,
            "nombre": farm.nombre,
            "veces_realizadas": farm.veces_realizadas,
            "ganancia_formateada": format_gsc(farm.ganancia),
            "creado_por": farm.creado_por,
            "waypoint": farm.waypoint,
            "duracion": farm.duracion,
            "requerimientos": farm.requerimientos,
            "profit_hr_formateado": format_gsc(farm.profit_hr) if farm.profit_hr is not None else '-',
            "limitation": farm.limitation
        })
    return render_template('admin_panel.html', farmeos=farmeos_formateados, pagination=pagination)

@main_bp.route('/admin/add', methods=['GET', 'POST'])
@login_required
def add_farm():
    if current_user.role not in ['admin', 'editor']:
        flash("No tienes permisos para añadir farmeos.")
        return redirect(url_for('main.index'))
    errors = []
    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        veces = request.form['veces_realizadas']
        g = request.form.get('gold', 0)
        s = request.form.get('silver', 0)
        c = request.form.get('copper', 0)
        waypoint = request.form.get('waypoint', '').strip()
        duracion = request.form.get('duracion', '').strip()
        # Validación de duración formato hh:mm:ss
        if duracion and not re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$', duracion):
            errors.append('La duración debe tener formato hh:mm:ss (ejemplo: 01:30:00)')
        requerimientos = request.form.get('requerimientos', '').strip()
        profit_hr_g = request.form.get('profit_hr_gold', 0)
        profit_hr_s = request.form.get('profit_hr_silver', 0)
        profit_hr_c = request.form.get('profit_hr_copper', 0)
        limitation = request.form.get('limitation', '').strip()
        datasets = request.form.get('datasets', '').strip()
        # Validaciones
        nombre_normalizado = nombre.lower().replace(' ', '')
        farmeo_existente = Farm.query.filter(db.func.replace(db.func.lower(Farm.nombre), ' ', '') == nombre_normalizado).first()
        if farmeo_existente:
            errors.append('Ya existe un farmeo con ese nombre (ignorando mayúsculas y espacios).')
        try:
            veces = int(veces)
            g = int(g)
            s = int(s)
            c = int(c)
            profit_hr_g = int(profit_hr_g)
            profit_hr_s = int(profit_hr_s)
            profit_hr_c = int(profit_hr_c)
            profit_hr = gsc_to_float(profit_hr_g, profit_hr_s, profit_hr_c)
        except ValueError:
            errors.append('Los valores numéricos deben ser números enteros.')
        else:
            if veces < 0:
                errors.append('Las veces realizadas no pueden ser negativas.')
            if g < 0 or s < 0 or c < 0:
                errors.append('No se permiten valores negativos en oro, plata o cobre.')
            if s > 99 or c > 99:
                errors.append('Plata y cobre deben estar entre 0 y 99.')
        if not errors:
            ganancia = gsc_to_float(g, s, c)
            nuevo_farm = Farm(
                nombre=nombre,
                veces_realizadas=veces,
                ganancia=ganancia,
                creado_por=current_user.username,
                waypoint=waypoint,
                duracion=duracion,
                requerimientos=requerimientos,
                profit_hr=profit_hr,
                limitation=limitation,
                datasets=datasets
            )
        db.session.add(nuevo_farm)
        db.session.commit()
        flash("Farmeo agregado correctamente.")
        return redirect(url_for('main.admin_panel'))
        # Si hay errores, no guardar y mostrar en el formulario
    return render_template('add_farm.html', errors=errors)

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
        farm.waypoint = request.form.get('waypoint', '').strip()
        farm.duracion = request.form.get('duracion', '').strip()
        farm.requerimientos = request.form.get('requerimientos', '').strip()
        profit_hr_g = request.form.get('profit_hr_gold', 0)
        profit_hr_s = request.form.get('profit_hr_silver', 0)
        profit_hr_c = request.form.get('profit_hr_copper', 0)
        try:
            farm.profit_hr = gsc_to_float(int(profit_hr_g), int(profit_hr_s), int(profit_hr_c))
        except ValueError:
            farm.profit_hr = None
        farm.limitation = request.form.get('limitation', '').strip()
        farm.datasets = request.form.get('datasets', '').strip()
        db.session.commit()
        flash("Farmeo actualizado correctamente.")
        return redirect(url_for('main.admin_panel'))

    # Para mostrar los valores en el formulario, extraemos G/S/C de la ganancia float
    total_cobre = int(round(farm.ganancia * 10000))
    farm.gold = total_cobre // 10000
    resto = total_cobre % 10000
    farm.silver = resto // 100
    farm.copper = resto % 100
    # Para mostrar los valores en el formulario, extraemos G/S/C de profit_hr
    if farm.profit_hr is not None:
        total_cobre_hr = int(round(farm.profit_hr * 10000))
        farm.profit_hr_gold = total_cobre_hr // 10000
        resto_hr = total_cobre_hr % 10000
        farm.profit_hr_silver = resto_hr // 100
        farm.profit_hr_copper = resto_hr % 100
    else:
        farm.profit_hr_gold = farm.profit_hr_silver = farm.profit_hr_copper = ''

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
    errors = []
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        role = request.form.get('role', 'user')
        if User.query.filter_by(username=username).first():
            errors.append('El usuario ya existe.')
        if len(password) < 6:
            errors.append('La contraseña debe tener al menos 6 caracteres.')
        if not errors:
            user = User(username=username, role=role)
            user.password = password
            db.session.add(user)
            db.session.commit()
            flash('Usuario creado correctamente.')
            return redirect(url_for('main.users_panel'))
        else:
            for e in errors:
                flash(e, 'error')
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

@main_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        actual = request.form['actual']
        nueva = request.form['nueva']
        repetir = request.form['repetir']
        if not current_user.check_password(actual):
            flash('La contraseña actual es incorrecta.', 'error')
        elif len(nueva) < 6:
            flash('La nueva contraseña debe tener al menos 6 caracteres.', 'error')
        elif nueva != repetir:
            flash('Las contraseñas nuevas no coinciden.', 'error')
        else:
            current_user.password = nueva
            db.session.commit()
            flash('Contraseña cambiada correctamente.', 'success')
            return redirect(url_for('main.index'))
    return render_template('change_password.html')

@main_bp.route('/admin/update_veces/<int:farm_id>', methods=['POST'])
@login_required
def update_veces_farm(farm_id):
    if current_user.role not in ['admin', 'editor']:
        return jsonify({'success': False, 'error': 'No autorizado'}), 403
    farm = Farm.query.get_or_404(farm_id)
    data = request.get_json()
    try:
        veces = int(data.get('veces_realizadas', -1))
        if veces < 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Valor inválido'}), 400
    farm.veces_realizadas = veces
    db.session.commit()
    return jsonify({'success': True, 'veces_realizadas': farm.veces_realizadas})

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    errors = []
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        if not username or not password:
            errors.append('Usuario y contraseña son obligatorios.')
        elif User.query.filter_by(username=username).first():
            errors.append('El usuario ya existe.')
        elif len(password) < 6:
            errors.append('La contraseña debe tener al menos 6 caracteres.')
        if not errors:
            user = User(username=username, role='user')
            user.password = password
            db.session.add(user)
            db.session.commit()
            flash('Cuenta creada correctamente. Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
        else:
            for e in errors:
                flash(e, 'error')
    return render_template('register.html')

@main_bp.app_errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@main_bp.app_errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

@main_bp.route('/farmeo/<int:farm_id>')
def farmeo_detail(farm_id):
    farm = Farm.query.get_or_404(farm_id)
    return render_template('farmeo_detail.html', farm=farm)

@main_bp.route('/robots.txt')
def robots_txt():
    lines = [
        'User-agent: *',
        'Disallow:',
        'Sitemap: ' + url_for('sitemap', _external=True)
    ]
    return '\n'.join(lines), 200, {'Content-Type': 'text/plain'}
