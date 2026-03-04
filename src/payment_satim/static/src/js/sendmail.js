/** @odoo-module **/


(function () {
    'use strict';

    const modalEl = document.getElementById('cibepay_input_email_box');
    const sendBtn = document.getElementById('cibepay_send_mail_btn');
    const emailInput = document.getElementById('cibepay_receiver_mail');
    const feedback = document.getElementById('cibepay_mail_feedback');

    /**
     * Show a Bootstrap-style alert inside the modal.
     * @param {string} message
     * @param {'success'|'danger'} type
     */
    function showFeedback(message, type) {
        feedback.className = 'mt-2 alert alert-' + type;
        feedback.textContent = message;
        feedback.style.display = 'block';
    }

    function hideFeedback() {
        feedback.style.display = 'none';
        feedback.textContent = '';
    }

    /** Reset modal state when it is hidden */
    modalEl.addEventListener('hidden.bs.modal', function () {
        emailInput.value = '';
        hideFeedback();
        setLoading(false);
    });

    /** Toggle the send button loading/disabled state */
    function setLoading(isLoading) {
        sendBtn.disabled = isLoading;
        sendBtn.innerHTML = isLoading
            ? '<i class="fa fa-spinner fa-spin me-1"></i><span>Envoi en cours…</span>'
            : '<i class="fa fa-envelope me-1"></i><span>Envoyer</span>';
    }

    function closeModal() {
        const dismissBtn = modalEl.querySelector('[data-bs-dismiss="modal"]');
        if (dismissBtn) {
            dismissBtn.click();
        }
    }

    sendBtn.addEventListener('click', async function () {
        hideFeedback();

        // Basic client-side validation
        if (!emailInput.validity.valid || !emailInput.value.trim()) {
            emailInput.classList.add('is-invalid');
            return;
        }
        emailInput.classList.remove('is-invalid');

        const email = emailInput.value.trim();
        setLoading(true);

        try {
            const url = '/shop/cibepay/sendbymail?receiver_mail=' + encodeURIComponent(email);
            const response = await fetch(url, {
                method: 'GET',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
            });

            if (!response.ok) {
                throw new Error('HTTP ' + response.status);
            }
            setLoading(false);
            closeModal();

        } catch (error) {
            console.error('[CibePay] sendbymail error:', error);
            showFeedback(
                "Une erreur est survenue lors de l'envoi. Veuillez réessayer.",
                'danger'
            );
            setLoading(false);
        }
    });
})();