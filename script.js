// ==========================================================================
// Green Minds - Day 1 JavaScript
// Handles UI interactions, input validation, and clean Day 1 confirmation
// (No fake AI results, no external APIs, no databases)
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const getStartedBtn = document.getElementById('getStartedBtn');
  const farmerForm = document.getElementById('farmerForm');
  const farmerNameInput = document.getElementById('farmerName');
  const stateSelect = document.getElementById('state');
  const districtInput = document.getElementById('district');
  const cropInput = document.getElementById('crop');
  const soilTypeSelect = document.getElementById('soilType');
  const weatherSelect = document.getElementById('weatherCondition');
  
  const submitBtn = document.getElementById('submitBtn');
  const loadingIndicator = document.getElementById('loadingIndicator');
  const errorBanner = document.getElementById('errorBanner');
  const errorMessage = document.getElementById('errorMessage');
  const adviceContainer = document.getElementById('adviceContainer');
  const adviceSubtitle = document.getElementById('adviceSubtitle');
  const adviceMeta = document.getElementById('adviceMeta');
  const adviceContent = document.getElementById('adviceContent');

  // Backend API URL: dynamically adapts to local development or cloud deployment
  const BACKEND_API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? (window.location.port === '5000' ? '/api/advice' : 'http://localhost:5000/api/advice')
    : '/api/advice';

  // Helper: Convert Gemini Markdown to readable HTML
  function renderMarkdownToHtml(markdownText) {
    if (!markdownText) return '';

    let html = markdownText
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    // Headings (### or ##)
    html = html.replace(/^###\s+(.*$)/gim, '<h4>🌱 $1</h4>');
    html = html.replace(/^##\s+(.*$)/gim, '<h4>🌿 $1</h4>');
    html = html.replace(/^#\s+(.*$)/gim, '<h4>🌾 $1</h4>');

    // Bold text (**text**)
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Numbered headings e.g. "1. Crop care advice"
    html = html.replace(/^(\d+)\.\s+\*\*(.*?)\*\*(.*$)/gim, '<h4>🌾 $1. $2</h4><p>$3</p>');
    html = html.replace(/^(\d+)\.\s+([^\n<]+)/gim, '<h4>🌾 $1. $2</h4>');

    // Bullet points (* or -)
    html = html.replace(/^\s*[\*\-]\s+(.*$)/gim, '<li>$1</li>');

    // Paragraph breaks
    const lines = html.split('\n');
    let inList = false;
    let result = '';

    lines.forEach(line => {
      const trimmed = line.trim();
      if (trimmed.startsWith('<li>')) {
        if (!inList) {
          result += '<ul>';
          inList = true;
        }
        result += trimmed;
      } else {
        if (inList) {
          result += '</ul>';
          inList = false;
        }
        if (trimmed && !trimmed.startsWith('<h4>') && !trimmed.startsWith('<ul>') && !trimmed.startsWith('</ul>')) {
          result += `<p>${trimmed}</p>`;
        } else if (trimmed) {
          result += trimmed;
        }
      }
    });

    if (inList) {
      result += '</ul>';
    }

    return result;
  }

  // 1. Smooth scroll to form when "Get Started" is clicked
  if (getStartedBtn) {
    getStartedBtn.addEventListener('click', (e) => {
      e.preventDefault();
      const formSection = document.getElementById('farmer-form-section');
      if (formSection) {
        formSection.scrollIntoView({ behavior: 'smooth' });
        setTimeout(() => {
          farmerNameInput.focus();
        }, 400);
      }
    });
  }

  // 2. Clear error state on input/change
  const inputFields = [
    farmerNameInput,
    stateSelect,
    districtInput,
    cropInput,
    soilTypeSelect,
    weatherSelect
  ];

  inputFields.forEach((field) => {
    if (!field) return;

    field.addEventListener('input', () => {
      clearFieldError(field);
    });

    field.addEventListener('change', () => {
      clearFieldError(field);
    });
  });

  function clearFieldError(field) {
    const formGroup = field.closest('.form-group');
    if (formGroup) {
      formGroup.classList.remove('has-error');
    }
  }

  function setFieldError(field) {
    const formGroup = field.closest('.form-group');
    if (formGroup) {
      formGroup.classList.add('has-error');
    }
  }

  // 3. Form submission: Connect to Gemini Backend
  farmerForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    let isValid = true;
    let firstInvalidField = null;

    // Validate inputs
    inputFields.forEach((field) => {
      if (!field.value || field.value.trim() === '') {
        setFieldError(field);
        isValid = false;
        if (!firstInvalidField) {
          firstInvalidField = field;
        }
      } else {
        clearFieldError(field);
      }
    });

    if (!isValid) {
      if (firstInvalidField) {
        firstInvalidField.focus();
      }
      return;
    }

    // Collect farmer information
    const farmerData = {
      name: farmerNameInput.value.trim(),
      state: stateSelect.value,
      district: districtInput.value.trim(),
      crop: cropInput.value.trim(),
      soilType: soilTypeSelect.value,
      weatherCondition: weatherSelect.value
    };

    // UI state: Reset existing results and show loading indicator
    if (adviceContainer) adviceContainer.classList.add('hidden');
    if (errorBanner) errorBanner.classList.add('hidden');
    if (loadingIndicator) loadingIndicator.classList.remove('hidden');

    // Disable submit button during request
    const originalBtnHtml = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span>Getting AI Advice...</span>`;

    // Scroll to loading indicator
    loadingIndicator.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    try {
      // Send details to Flask backend (which securely contacts Gemini)
      const response = await fetch(BACKEND_API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(farmerData)
      });

      const data = await response.json();

      if (response.ok && data.success) {
        // Populate farmer details in summary pills
        if (adviceMeta) {
          adviceMeta.innerHTML = `
            <div class="status-meta-item">
              <span class="meta-label">Farmer</span>
              <span class="meta-val">${farmerData.name}</span>
            </div>
            <div class="status-meta-item">
              <span class="meta-label">Location</span>
              <span class="meta-val">${farmerData.district}, ${farmerData.state}</span>
            </div>
            <div class="status-meta-item">
              <span class="meta-label">Crop</span>
              <span class="meta-val">${farmerData.crop}</span>
            </div>
            <div class="status-meta-item">
              <span class="meta-label">Soil</span>
              <span class="meta-val">${farmerData.soilType}</span>
            </div>
            <div class="status-meta-item">
              <span class="meta-label">Weather</span>
              <span class="meta-val">${farmerData.weatherCondition}</span>
            </div>
          `;
        }

        if (adviceSubtitle) {
          adviceSubtitle.textContent = `Personalized for ${farmerData.name} • ${farmerData.crop} cultivation in ${farmerData.district}`;
        }

        // Render formatted Gemini advice
        if (adviceContent) {
          adviceContent.innerHTML = renderMarkdownToHtml(data.advice);
        }

        // Display advice card
        if (adviceContainer) {
          adviceContainer.classList.remove('hidden');
          adviceContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      } else {
        // Show error returned by backend
        const errMsg = data.error || 'Server responded with an error.';
        showError(errMsg);
      }
    } catch (err) {
      // Network or connection error (e.g. backend server is not running)
      const connectionErrorMsg =
        window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
          ? 'Could not connect to the backend server (http://localhost:5000). Please make sure "python server.py" is running in your terminal.'
          : 'Could not connect to the Green Minds backend service. Please check your internet connection and verify that the server is online.';
      showError(connectionErrorMsg);
      console.error('Fetch error:', err);
    } finally {
      // Hide loading indicator and re-enable button
      if (loadingIndicator) loadingIndicator.classList.add('hidden');
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalBtnHtml;
    }
  });

  function showError(msg) {
    if (errorMessage) {
      errorMessage.textContent = msg;
    }
    if (errorBanner) {
      errorBanner.classList.remove('hidden');
      errorBanner.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }
});
