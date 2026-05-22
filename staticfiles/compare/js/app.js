'use strict';

function showToast(message) {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.querySelector('div').textContent = message;
    toast.classList.remove('translate-y-20', 'opacity-0');
    toast.classList.add('translate-y-0', 'opacity-100');
    clearTimeout(showToast._timer);
    showToast._timer = setTimeout(() => {
        toast.classList.add('translate-y-20', 'opacity-0');
        toast.classList.remove('translate-y-0', 'opacity-100');
    }, 2500);
}

function copyInviteLink() {
    const input = document.getElementById('invite-link');
    if (!input) return;
    navigator.clipboard.writeText(input.value).then(() => {
        const btn = document.getElementById('copy-btn');
        if (btn) {
            const original = btn.textContent;
            btn.textContent = 'Copied!';
            btn.classList.add('bg-emerald-600', 'hover:bg-emerald-600');
            btn.classList.remove('bg-brand-600', 'hover:bg-brand-700');
            setTimeout(() => {
                btn.textContent = original;
                btn.classList.remove('bg-emerald-600', 'hover:bg-emerald-600');
                btn.classList.add('bg-brand-600', 'hover:bg-brand-700');
            }, 2000);
        }
        showToast('Invite link copied to clipboard');
    });
}

function initFileUploads() {
    document.querySelectorAll('[data-file-upload]').forEach((zone) => {
        const input = zone.querySelector('input[type="file"]');
        const label = zone.querySelector('[data-file-label]');
        if (!input || !label) return;

        const defaultText = label.textContent;

        const updateLabel = () => {
            if (input.files && input.files.length > 0) {
                label.textContent = input.files[0].name;
                zone.classList.add('border-brand-500', 'bg-brand-50');
            } else {
                label.textContent = defaultText;
                zone.classList.remove('border-brand-500', 'bg-brand-50');
            }
        };

        input.addEventListener('change', updateLabel);

        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            zone.classList.add('border-brand-500', 'bg-brand-50');
        });

        zone.addEventListener('dragleave', () => {
            if (!input.files || input.files.length === 0) {
                zone.classList.remove('border-brand-500', 'bg-brand-50');
            }
        });

        zone.addEventListener('drop', (e) => {
            e.preventDefault();
            if (e.dataTransfer.files.length) {
                input.files = e.dataTransfer.files;
                updateLabel();
            }
        });
    });
}

document.addEventListener('DOMContentLoaded', initFileUploads);
