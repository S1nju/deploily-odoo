# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request


class BookingController(http.Controller):

    @http.route('/booking', type='http', auth='public', website=False)
    def booking_page_default(self, **kwargs):
        """Redirect to main booking page."""
        return self.booking_page(**kwargs)

    @http.route('/booking/<string:token>', type='http', auth='public', website=False)
    def booking_page(self, token=None, **kwargs):
        """Serve the booking HTML page."""
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return request.make_response(
            self._get_booking_html(base_url),
            headers=[('Content-Type', 'text/html; charset=utf-8')]
        )

    @http.route('/booking/api/available-dates', type='json', auth='public', csrf=False)
    def get_available_dates(self, **kwargs):
        """Return list of available and unavailable dates."""
        slots = request.env['appointment.slot'].sudo().search([])
        result = []
        for slot in slots:
            result.append({
                'date': str(slot.date),
                'is_available': slot.is_available,
                'appointment_count': slot.appointment_count,
                'note': slot.note or '',
            })
        return result

    @http.route('/booking/api/submit', type='json', auth='public', csrf=False)
    def submit_booking(self, **kwargs):
        """Handle booking form submission."""
        data = kwargs

        required = ['client_name', 'client_email', 'date_appointment']
        for field in required:
            if not data.get(field):
                return {'success': False, 'error': f'Champ requis manquant: {field}'}

        # Check date is still available
        date = data.get('date_appointment')
        slot = request.env['appointment.slot'].sudo().search(
            [('date', '=', date), ('is_available', '=', True)], limit=1
        )

        try:
            appointment_vals = {
                'client_name': data.get('client_name', ''),
                'client_email': data.get('client_email', ''),
                'client_phone': data.get('client_phone', ''),
                'client_company': data.get('client_company', ''),
                'reason': data.get('reason', ''),
                'date_appointment': date,
                'state': 'new',
            }
            if slot:
                appointment_vals['slot_id'] = slot.id

            appointment = request.env['appointment.appointment'].sudo().create(appointment_vals)

            return {
                'success': True,
                'appointment_id': appointment.id,
                'reference': appointment.name,
                'message': f'Votre rendez-vous du {date} a été confirmé. Un email de confirmation vous a été envoyé.'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _get_booking_html(self, base_url):
        """Return the full booking page HTML."""
        return '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prendre un Rendez-vous</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 30px 15px;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            color: white;
            margin-bottom: 35px;
        }

        .header h1 {
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 8px;
        }

        .header p {
            font-size: 1.05rem;
            opacity: 0.85;
        }

        .card {
            background: white;
            border-radius: 20px;
            padding: 35px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
            margin-bottom: 25px;
        }

        .card h2 {
            font-size: 1.3rem;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 2px solid #f0f0f0;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        /* CALENDAR */
        .calendar-nav {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 18px;
        }

        .calendar-nav button {
            background: #667eea;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 8px 18px;
            font-size: 1.1rem;
            cursor: pointer;
            transition: background 0.2s;
        }

        .calendar-nav button:hover { background: #5a6fd6; }

        .calendar-nav h3 {
            font-size: 1.2rem;
            color: #333;
            text-transform: capitalize;
        }

        .calendar-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 6px;
        }

        .day-header {
            text-align: center;
            font-weight: 600;
            color: #888;
            font-size: 0.8rem;
            padding: 6px 0;
            text-transform: uppercase;
        }

        .day-cell {
            aspect-ratio: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            border-radius: 10px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 500;
            transition: all 0.2s;
            position: relative;
            border: 2px solid transparent;
        }

        .day-cell.empty { cursor: default; }

        .day-cell.past {
            color: #ccc;
            cursor: not-allowed;
        }

        .day-cell.unavailable {
            background: #fff0f0;
            color: #ffaaaa;
            cursor: not-allowed;
        }

        .day-cell.available {
            background: #f0fff4;
            color: #27ae60;
        }

        .day-cell.available:hover {
            background: #27ae60;
            color: white;
            transform: scale(1.08);
        }

        .day-cell.selected {
            background: #667eea !important;
            color: white !important;
            border-color: #4a5dc7;
            transform: scale(1.08);
        }

        .day-cell.today {
            border-color: #667eea;
        }

        .dot {
            width: 5px;
            height: 5px;
            border-radius: 50%;
            background: #e74c3c;
            position: absolute;
            bottom: 4px;
        }

        .day-cell.available .dot { background: #27ae60; }
        .day-cell.selected .dot { background: white; }

        /* LEGEND */
        .legend {
            display: flex;
            gap: 20px;
            margin-top: 15px;
            flex-wrap: wrap;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 7px;
            font-size: 0.85rem;
            color: #666;
        }

        .legend-dot {
            width: 14px;
            height: 14px;
            border-radius: 4px;
        }

        /* FORM */
        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 18px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .form-group.full { grid-column: 1 / -1; }

        label {
            font-size: 0.88rem;
            font-weight: 600;
            color: #555;
        }

        label .required { color: #e74c3c; margin-left: 3px; }

        input, textarea {
            padding: 12px 15px;
            border: 2px solid #e8e8e8;
            border-radius: 10px;
            font-size: 0.95rem;
            color: #333;
            transition: border-color 0.2s;
            font-family: inherit;
        }

        input:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }

        textarea { resize: vertical; min-height: 90px; }

        .selected-date-display {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-radius: 12px;
            padding: 15px 20px;
            text-align: center;
            margin-bottom: 20px;
            font-size: 1.05rem;
            font-weight: 600;
        }

        .btn-submit {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1.05rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 10px;
            letter-spacing: 0.5px;
        }

        .btn-submit:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102,126,234,0.4);
        }

        .btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }

        /* SUCCESS STATE */
        .success-box {
            text-align: center;
            padding: 40px 20px;
            display: none;
        }

        .success-icon {
            font-size: 4rem;
            margin-bottom: 20px;
        }

        .success-box h2 {
            color: #27ae60;
            font-size: 1.8rem;
            margin-bottom: 12px;
            border: none;
            padding: 0;
        }

        .success-box p {
            color: #666;
            font-size: 1rem;
            line-height: 1.6;
        }

        .reference-badge {
            background: #f0fff4;
            border: 2px solid #27ae60;
            border-radius: 10px;
            padding: 12px 20px;
            display: inline-block;
            margin: 15px 0;
            font-weight: 700;
            color: #27ae60;
            font-size: 1.1rem;
        }

        .error-msg {
            background: #fff0f0;
            border: 1px solid #ffcccc;
            color: #e74c3c;
            padding: 12px 15px;
            border-radius: 8px;
            margin-top: 10px;
            font-size: 0.9rem;
            display: none;
        }

        .form-section { display: block; }

        @media (max-width: 600px) {
            .form-grid { grid-template-columns: 1fr; }
            .header h1 { font-size: 1.6rem; }
            .card { padding: 20px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📅 Prendre un Rendez-vous</h1>
            <p>Choisissez une date disponible et remplissez le formulaire</p>
        </div>

        <!-- CALENDAR CARD -->
        <div class="card" id="calendarCard">
            <h2>📆 Choisir une date</h2>
            <div class="calendar-nav">
                <button onclick="changeMonth(-1)">&#8249;</button>
                <h3 id="monthTitle"></h3>
                <button onclick="changeMonth(1)">&#8250;</button>
            </div>
            <div class="calendar-grid" id="calendarGrid">
                <div class="day-header">Lun</div>
                <div class="day-header">Mar</div>
                <div class="day-header">Mer</div>
                <div class="day-header">Jeu</div>
                <div class="day-header">Ven</div>
                <div class="day-header">Sam</div>
                <div class="day-header">Dim</div>
            </div>
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-dot" style="background:#f0fff4; border:2px solid #27ae60;"></div>
                    Disponible
                </div>
                <div class="legend-item">
                    <div class="legend-dot" style="background:#fff0f0; border:2px solid #ffaaaa;"></div>
                    Indisponible
                </div>
                <div class="legend-item">
                    <div class="legend-dot" style="background:#667eea;"></div>
                    Sélectionné
                </div>
            </div>
        </div>

        <!-- FORM CARD -->
        <div class="card" id="formCard" style="display:none;">
            <div class="success-box" id="successBox">
                <div class="success-icon">✅</div>
                <h2>Rendez-vous confirmé !</h2>
                <div class="reference-badge" id="refBadge"></div>
                <p>Un email de confirmation a été envoyé à votre adresse.<br>Nous vous contacterons bientôt pour confirmer les détails.</p>
            </div>

            <div class="form-section" id="formSection">
                <h2>✏️ Vos informations</h2>
                <div class="selected-date-display" id="selectedDateDisplay"></div>

                <div class="form-grid">
                    <div class="form-group">
                        <label>Nom complet <span class="required">*</span></label>
                        <input type="text" id="clientName" placeholder="Ahmed Benali">
                    </div>
                    <div class="form-group">
                        <label>Email <span class="required">*</span></label>
                        <input type="email" id="clientEmail" placeholder="ahmed@exemple.com">
                    </div>
                    <div class="form-group">
                        <label>Téléphone</label>
                        <input type="tel" id="clientPhone" placeholder="+213 555 123 456">
                    </div>
                    <div class="form-group">
                        <label>Société</label>
                        <input type="text" id="clientCompany" placeholder="Nom de votre société">
                    </div>
                    <div class="form-group full">
                        <label>Raison / Message</label>
                        <textarea id="reason" placeholder="Décrivez brièvement la raison de votre rendez-vous..."></textarea>
                    </div>
                </div>

                <div class="error-msg" id="errorMsg"></div>
                <button class="btn-submit" id="submitBtn" onclick="submitForm()">
                    Confirmer le rendez-vous
                </button>
            </div>
        </div>
    </div>

<script>
    const BASE_URL = "''' + base_url + '''";
    let currentDate = new Date();
    let selectedDate = null;
    let availableDates = {};

    const MONTHS_FR = [
        'Janvier','Février','Mars','Avril','Mai','Juin',
        'Juillet','Août','Septembre','Octobre','Novembre','Décembre'
    ];

    // Load available dates from Odoo
    async function loadAvailableDates() {
        try {
            const resp = await fetch(BASE_URL + '/booking/api/available-dates', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({jsonrpc:'2.0',method:'call',params:{}})
            });
            const data = await resp.json();
            const slots = data.result || [];
            slots.forEach(slot => {
                availableDates[slot.date] = slot;
            });
        } catch(e) {
            console.log('Could not load dates:', e);
        }
        renderCalendar();
    }

    function changeMonth(dir) {
        currentDate.setMonth(currentDate.getMonth() + dir);
        renderCalendar();
    }

    function renderCalendar() {
        const year = currentDate.getFullYear();
        const month = currentDate.getMonth();
        const today = new Date();
        today.setHours(0,0,0,0);

        document.getElementById('monthTitle').textContent =
            MONTHS_FR[month] + ' ' + year;

        const grid = document.getElementById('calendarGrid');
        // Keep headers
        while (grid.children.length > 7) grid.removeChild(grid.lastChild);

        const firstDay = new Date(year, month, 1);
        // Monday=0 offset
        let startOffset = firstDay.getDay() - 1;
        if (startOffset < 0) startOffset = 6;

        for (let i = 0; i < startOffset; i++) {
            const empty = document.createElement('div');
            empty.className = 'day-cell empty';
            grid.appendChild(empty);
        }

        const daysInMonth = new Date(year, month + 1, 0).getDate();
        for (let d = 1; d <= daysInMonth; d++) {
            const cell = document.createElement('div');
            const dateStr = `${year}-${String(month+1).padStart(2,'0')}-${String(d).padStart(2,'0')}`;
            const cellDate = new Date(year, month, d);
            cellDate.setHours(0,0,0,0);

            cell.classList.add('day-cell');
            cell.textContent = d;

            if (cellDate < today) {
                cell.classList.add('past');
            } else if (availableDates[dateStr] && availableDates[dateStr].is_available) {
                cell.classList.add('available');
                if (availableDates[dateStr].appointment_count > 0) {
                    const dot = document.createElement('div');
                    dot.className = 'dot';
                    cell.appendChild(dot);
                }
                cell.onclick = () => selectDate(dateStr, cell);
            } else if (availableDates[dateStr] && !availableDates[dateStr].is_available) {
                cell.classList.add('unavailable');
                if (availableDates[dateStr].appointment_count > 0) {
                    const dot = document.createElement('div');
                    dot.className = 'dot';
                    cell.appendChild(dot);
                }
            } else {
                // No slot defined = available by default (no restriction)
                cell.classList.add('available');
                cell.onclick = () => selectDate(dateStr, cell);
            }

            if (cellDate.toDateString() === today.toDateString()) {
                cell.classList.add('today');
            }

            if (selectedDate === dateStr) {
                cell.classList.add('selected');
            }

            grid.appendChild(cell);
        }
    }

    function selectDate(dateStr, cell) {
        // Deselect previous
        document.querySelectorAll('.day-cell.selected').forEach(c => c.classList.remove('selected'));
        cell.classList.add('selected');
        selectedDate = dateStr;

        // Format date in French
        const parts = dateStr.split('-');
        const dateObj = new Date(parseInt(parts[0]), parseInt(parts[1])-1, parseInt(parts[2]));
        const formatted = dateObj.toLocaleDateString('fr-FR', {
            weekday:'long', year:'numeric', month:'long', day:'numeric'
        });

        document.getElementById('selectedDateDisplay').textContent = '📅 ' + formatted.charAt(0).toUpperCase() + formatted.slice(1);
        document.getElementById('formCard').style.display = 'block';
        document.getElementById('formCard').scrollIntoView({behavior:'smooth', block:'start'});
    }

    async function submitForm() {
        const name = document.getElementById('clientName').value.trim();
        const email = document.getElementById('clientEmail').value.trim();
        const phone = document.getElementById('clientPhone').value.trim();
        const company = document.getElementById('clientCompany').value.trim();
        const reason = document.getElementById('reason').value.trim();
        const errorEl = document.getElementById('errorMsg');

        errorEl.style.display = 'none';

        if (!name) { showError('Veuillez entrer votre nom.'); return; }
        if (!email || !email.includes('@')) { showError('Veuillez entrer un email valide.'); return; }
        if (!selectedDate) { showError('Veuillez sélectionner une date.'); return; }

        const btn = document.getElementById('submitBtn');
        btn.disabled = true;
        btn.textContent = 'Envoi en cours...';

        try {
            const resp = await fetch(BASE_URL + '/booking/api/submit', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    jsonrpc: '2.0', method: 'call',
                    params: {
                        client_name: name,
                        client_email: email,
                        client_phone: phone,
                        client_company: company,
                        reason: reason,
                        date_appointment: selectedDate,
                    }
                })
            });

            const data = await resp.json();
            const result = data.result;

            if (result && result.success) {
                document.getElementById('formSection').style.display = 'none';
                document.getElementById('successBox').style.display = 'block';
                document.getElementById('refBadge').textContent = 'Référence: ' + result.reference;
            } else {
                showError(result ? result.error : 'Une erreur est survenue. Veuillez réessayer.');
                btn.disabled = false;
                btn.textContent = 'Confirmer le rendez-vous';
            }
        } catch(e) {
            showError('Erreur de connexion. Veuillez réessayer.');
            btn.disabled = false;
            btn.textContent = 'Confirmer le rendez-vous';
        }
    }

    function showError(msg) {
        const el = document.getElementById('errorMsg');
        el.textContent = msg;
        el.style.display = 'block';
    }

    // Init
    loadAvailableDates();
</script>
</body>
</html>'''
