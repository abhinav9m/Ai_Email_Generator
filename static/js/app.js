document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const emailForm = document.getElementById('email-form');
  const selectPurpose = document.getElementById('select-purpose');
  const inputRecipient = document.getElementById('input-recipient');
  const inputSender = document.getElementById('input-sender');
  const userMessage = document.getElementById('user-message');
  const btnGenerate = document.getElementById('btn-generate');

  const tonePills = document.querySelectorAll('#tone-pills .pill-btn');
  const lengthPills = document.querySelectorAll('#length-pills .pill-btn');

  const outputBox = document.getElementById('output-box');
  const emptyState = document.getElementById('empty-state');
  const generatedView = document.getElementById('generated-view');
  const outputSubject = document.getElementById('output-subject');
  const outputFullText = document.getElementById('output-full-text');
  const copyToolbar = document.getElementById('copy-toolbar');
  const refineContainer = document.getElementById('refine-container');
  const apiWarningBadge = document.getElementById('api-warning-badge');

  const btnCopySubject = document.getElementById('btn-copy-subject');
  const btnCopySubIcon = document.getElementById('btn-copy-sub-icon');
  const btnCopyFull = document.getElementById('btn-copy-full');
  const btnExportTxt = document.getElementById('btn-export-txt');

  const btnRegenerateNew = document.getElementById('btn-regenerate-new');
  const btnRefineShorter = document.getElementById('btn-refine-shorter');
  const btnRefineFormal = document.getElementById('btn-refine-formal');
  const btnRefineFriendly = document.getElementById('btn-refine-friendly');
  const btnRefineGrammar = document.getElementById('btn-refine-grammar');
  const btnRefineCustom = document.getElementById('btn-refine-custom');
  const customRefineInput = document.getElementById('custom-refine-input');

  const btnSample1 = document.getElementById('btn-sample-1');
  const btnSample2 = document.getElementById('btn-sample-2');
  
  const historyList = document.getElementById('history-list');
  const historyCount = document.getElementById('history-count');
  const btnClearHistory = document.getElementById('btn-clear-history');

  // App State
  let currentTone = 'Professional';
  let currentLength = 'Medium';
  let currentEmailData = null;

  // Toast notification helper
  function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <i class="fa-solid ${type === 'success' ? 'fa-circle-check' : type === 'error' ? 'fa-circle-exclamation' : 'fa-circle-info'}"></i>
      <span>${message}</span>
    `;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  function setPillActive(pills, targetValue) {
    pills.forEach(p => {
      if (p.dataset.value === targetValue) {
        p.classList.add('active');
      } else {
        p.classList.remove('active');
      }
    });
  }

  // Pill click handlers
  tonePills.forEach(pill => {
    pill.addEventListener('click', () => {
      tonePills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      currentTone = pill.dataset.value;
    });
  });

  lengthPills.forEach(pill => {
    pill.addEventListener('click', () => {
      lengthPills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      currentLength = pill.dataset.value;
    });
  });

  // Sample prompt loaders (Requirement #12)
  btnSample1.addEventListener('click', () => {
    selectPurpose.value = 'Leave Request';
    inputRecipient.value = 'Manager';
    inputSender.value = 'Abhinav';
    currentTone = 'Professional';
    currentLength = 'Medium';
    setPillActive(tonePills, 'Professional');
    setPillActive(lengthPills, 'Medium');
    userMessage.value = 'I need to request 3 days of leave for a personal appointment.';
    showToast('Loaded Sample Leave Request', 'info');
  });

  btnSample2.addEventListener('click', () => {
    selectPurpose.value = 'Internship Request';
    inputRecipient.value = 'HR Team';
    inputSender.value = 'Abhinav';
    currentTone = 'Professional';
    currentLength = 'Medium';
    setPillActive(tonePills, 'Professional');
    setPillActive(lengthPills, 'Medium');
    userMessage.value = 'I am a Computer Science Engineering student interested in an internship opportunity.';
    showToast('Loaded Sample Internship Request', 'info');
  });

  // Render Output Display
  function renderEmailOutput(data) {
    currentEmailData = data;
    emptyState.style.display = 'none';
    generatedView.style.display = 'flex';
    copyToolbar.style.display = 'flex';
    refineContainer.style.display = 'flex';

    outputSubject.textContent = data.subject || 'No subject';
    
    // Construct email format for visual editor
    const formatted = `${data.greeting || ''}\n\n${data.body || ''}\n\n${data.closing || ''}`;
    outputFullText.textContent = formatted;

    if (data.api_warning) {
      apiWarningBadge.style.display = 'inline';
      apiWarningBadge.textContent = data.api_warning;
    } else {
      apiWarningBadge.style.display = 'none';
    }
  }

  // Generate Email Form Submission (Requirement #11 Validation)
  emailForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    await executeGeneration();
  });

  async function executeGeneration(isRegenerate = false) {
    const purpose = selectPurpose.value;
    const recipient = inputRecipient.value.trim();
    const sender = inputSender.value.trim();
    const message = userMessage.value.trim();

    if (!purpose) {
      showToast('Please select an Email Purpose / Category!', 'error');
      return;
    }

    if (!message || message.length < 3) {
      showToast('Please enter your main message content and key points!', 'error');
      return;
    }

    // UI Loading state
    btnGenerate.disabled = true;
    if (btnRegenerateNew) btnRegenerateNew.disabled = true;
    btnGenerate.innerHTML = `<span class="spinner"></span> Generating...`;

    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          purpose,
          recipient: recipient || "Recipient",
          tone: currentTone,
          length: currentLength,
          user_message: message,
          sender_name: sender
        })
      });

      const resData = await response.json();
      if (response.ok && resData.status === 'success') {
        renderEmailOutput(resData.data);
        showToast(isRegenerate ? 'Regenerated new version!' : 'Email generated successfully!', 'success');
        loadHistory();
      } else {
        throw new Error(resData.detail || 'Failed to generate email.');
      }
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      btnGenerate.disabled = false;
      if (btnRegenerateNew) btnRegenerateNew.disabled = false;
      btnGenerate.innerHTML = `<i class="fa-solid fa-bolt"></i> Generate Email`;
    }
  }

  // Regenerate New Version Button (Requirement #8)
  if (btnRegenerateNew) {
    btnRegenerateNew.addEventListener('click', () => {
      executeGeneration(true);
    });
  }

  // Refine / Improve handler helper (Requirement #9)
  async function triggerRefine(action, customInstruction = null) {
    if (!currentEmailData) {
      showToast('No email available to improve.', 'error');
      return;
    }

    const textLines = outputFullText.textContent.split('\n\n');
    const currentGreeting = textLines[0] || currentEmailData.greeting || '';
    const currentClosing = textLines[textLines.length - 1] || currentEmailData.closing || '';
    const currentBody = textLines.slice(1, textLines.length - 1).join('\n\n') || currentEmailData.body || outputFullText.textContent;

    showToast(`Improving email (${action})...`, 'info');

    try {
      const response = await fetch('/api/refine', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subject: outputSubject.textContent,
          greeting: currentGreeting,
          body: currentBody,
          closing: currentClosing,
          action: action,
          custom_instruction: customInstruction,
          purpose: currentEmailData.purpose || selectPurpose.value,
          recipient: inputRecipient.value.trim(),
          sender_name: inputSender.value.trim(),
          user_message: userMessage.value.trim()
        })
      });

      const resData = await response.json();
      if (response.ok && resData.status === 'success') {
        renderEmailOutput(resData.data);
        showToast('Improved version created and saved to history!', 'success');
        loadHistory();
      } else {
        throw new Error(resData.detail || 'Failed to improve email.');
      }
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  btnRefineShorter.addEventListener('click', () => triggerRefine('shorter'));
  btnRefineFormal.addEventListener('click', () => triggerRefine('formal'));
  btnRefineFriendly.addEventListener('click', () => triggerRefine('friendlier'));
  btnRefineGrammar.addEventListener('click', () => triggerRefine('grammar'));

  btnRefineCustom.addEventListener('click', () => {
    const customText = customRefineInput.value.trim();
    if (!customText) {
      showToast('Enter custom improvement instruction', 'error');
      return;
    }
    triggerRefine('custom', customText);
    customRefineInput.value = '';
  });

  // Copy Actions
  function copyToClipboard(text, label) {
    navigator.clipboard.writeText(text).then(() => {
      showToast(`${label} copied to clipboard!`, 'success');
    }).catch(() => {
      showToast(`Failed to copy ${label}`, 'error');
    });
  }

  btnCopySubject.addEventListener('click', () => copyToClipboard(outputSubject.textContent, 'Subject'));
  btnCopySubIcon.addEventListener('click', () => copyToClipboard(outputSubject.textContent, 'Subject'));
  
  btnCopyFull.addEventListener('click', () => {
    const fullText = `Subject: ${outputSubject.textContent}\n\n${outputFullText.textContent}`;
    copyToClipboard(fullText, 'Full Email');
  });

  // Export .txt file
  btnExportTxt.addEventListener('click', () => {
    if (!outputSubject.textContent) return;
    const fullText = `Subject: ${outputSubject.textContent}\n\n${outputFullText.textContent}`;
    const blob = new Blob([fullText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `email_${outputSubject.textContent.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('Exported email to file', 'success');
  });

  // Format date helper (Requirement #10)
  function formatDate(dateStr) {
    if (!dateStr) return '';
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) + ', ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return dateStr;
    }
  }

  // Load History from SQLite (Requirement #7 & #10)
  async function loadHistory() {
    try {
      const response = await fetch('/api/history');
      const resData = await response.json();

      if (response.ok && resData.status === 'success') {
        const historyItems = resData.data;
        historyCount.textContent = `${historyItems.length} Saved`;

        if (historyItems.length === 0) {
          historyList.innerHTML = `<p style="color: var(--text-muted); font-size: 0.9rem; grid-column: 1 / -1; text-align: center; padding: 1.5rem;">No saved history yet.</p>`;
          return;
        }

        historyList.innerHTML = '';
        historyItems.forEach(item => {
          const card = document.createElement('div');
          card.className = 'history-card';
          
          const recipDisplay = item.recipient ? `To: ${item.recipient}` : 'To: Recipient';
          const versionTag = item.version && item.version > 1 ? `<span class="badge" style="background: rgba(16, 185, 129, 0.2); color: #6ee7b7; margin-left: 4px;">v${item.version}</span>` : '';

          card.innerHTML = `
            <div class="history-header">
              <div>
                <span class="badge">${item.purpose || 'Email'}</span>
                ${versionTag}
              </div>
              <div style="display: flex; gap: 4px; align-items: center;">
                <button class="icon-btn copy-card-btn" data-id="${item.id}" title="Copy Full Email">
                  <i class="fa-regular fa-copy"></i>
                </button>
                <button class="icon-btn fav ${item.is_favorite ? 'fav-active' : ''}" data-id="${item.id}" title="Toggle Favorite">
                  <i class="${item.is_favorite ? 'fa-solid' : 'fa-regular'} fa-star"></i>
                </button>
                <button class="icon-btn delete-btn" data-id="${item.id}" title="Delete">
                  <i class="fa-solid fa-trash"></i>
                </button>
              </div>
            </div>
            <div style="font-size: 0.78rem; color: #a5b4fc; font-weight: 500;">${recipDisplay}</div>
            <div class="history-subject">${item.subject}</div>
            <div class="history-snippet">${item.body}</div>
            <div class="history-footer">
              <span>${item.tone || 'Professional'} • ${item.length || 'Medium'}</span>
              <span>${formatDate(item.created_at)}</span>
            </div>
          `;

          // Card click loads into output editor
          card.addEventListener('click', (e) => {
            if (e.target.closest('.icon-btn')) return;
            
            // Refill form controls
            if (item.purpose) selectPurpose.value = item.purpose;
            if (item.recipient) inputRecipient.value = item.recipient;
            if (item.user_name) inputSender.value = item.user_name;
            if (item.user_message) userMessage.value = item.user_message;
            if (item.tone) {
              currentTone = item.tone;
              setPillActive(tonePills, item.tone);
            }
            if (item.length) {
              currentLength = item.length;
              setPillActive(lengthPills, item.length);
            }

            renderEmailOutput({
              subject: item.subject,
              greeting: item.greeting,
              body: item.body,
              closing: item.closing,
              full_email: item.full_email,
              purpose: item.purpose
            });
            showToast('Loaded email from history', 'info');
          });

          // Copy card email
          const copyCardBtn = card.querySelector('.copy-card-btn');
          copyCardBtn.addEventListener('click', () => {
            copyToClipboard(item.full_email || `Subject: ${item.subject}\n\n${item.body}`, 'Email');
          });

          // Favorite toggle
          const favBtn = card.querySelector('.fav');
          favBtn.addEventListener('click', async () => {
            await fetch(`/api/history/${item.id}/favorite`, { method: 'POST' });
            loadHistory();
          });

          // Delete single item
          const delBtn = card.querySelector('.delete-btn');
          delBtn.addEventListener('click', async () => {
            await fetch(`/api/history/${item.id}`, { method: 'DELETE' });
            showToast('Deleted item from history', 'info');
            loadHistory();
          });

          historyList.appendChild(card);
        });
      }
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  }

  // Clear All History with Confirmation (Requirement #10)
  btnClearHistory.addEventListener('click', async () => {
    if (confirm('Are you sure you want to clear all stored email history? This action cannot be undone.')) {
      await fetch('/api/history', { method: 'DELETE' });
      showToast('All history cleared', 'info');
      loadHistory();
    }
  });

  // Initial Load
  loadHistory();
});
