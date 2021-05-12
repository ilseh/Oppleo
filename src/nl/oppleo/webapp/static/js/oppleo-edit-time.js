/* 
  Oppleo Edit Time Web Component

  Import the following in the main file

  <!-- https://timepicker.co/ -->
  <link href="/static/plugins/timepicker/1.3.5/jquery.timepicker.min.css" rel="stylesheet" type="text/css" />
  <script src="/static/plugins/timepicker/1.3.5/jquery.timepicker.min.js" type="text/javascript"></script>


  Options:


*/



class OppleoEditTime extends HTMLElement {
  constructor() {
    super()

    // querySelector does not allow ID's staring with a digit!!!
    this.elId = "id_" + Math.random().toString(36).substr(2, 8)
    this.oppleo_edit_time_template = document.createElement('template');

    this.oppleo_edit_time_template.innerHTML = `
      <!-- App css -->
      <link rel="stylesheet" type="text/css" href="/static/plugins/bootstrap/4.4.1/css/bootstrap.min.css">
      <link rel="stylesheet" type="text/css" href="/static/css/icons.css">
      <link rel="stylesheet" type="text/css" href="/static/css/style.css">
    
      <script src="/static/js/jquery-3.3.1.js"></script>
      
      <script src="/static/plugins/bootstrap/4.4.1/js/bootstrap.min.js"></script>
      <script src="/static/js/waves.js"></script>
    
      <link rel="stylesheet" type="text/css" href="/static/plugins/fontawesome/5.13.3/css/all.min.css">
      <style>
      button {
        cursor: pointer;
      }
      .btn-low-key-warning {
          color: #868e96;
          background-color: transparent;
          background-image: none;
          border-color: #868e96;
      }
      .btn-low-key-warning:hover, .btn-low-key-warning:focus, .btn-low-key-warning:active, .btn-low-key-warning.active, .open>.dropdown-toggle.btn-low-key-warning {
          color: #fff;
          background-color: #ffaa00;
          background-image: none;
          border-color: #ffaa00;
      }
      .form-control {
        color: #ffffff !important;
        background-color: #434f5c;
      }
      .form-control:disabled, .form-control[readonly] {
        color: #3bafda !important;
        background-color: rgba(0,0,0,.05) !important;
      }
      .input-group {
        position: relative;
        display: flex;
        flex-wrap: wrap; // For form validation feedback
        align-items: stretch;
        width: 100%;
      }
      span.input-group-text-icon {
        border: 1px solid #4c5a67;
        border-left: 0px;
        border-right: 0px;

        border-radius: 0.1rem;
        display: flex;
        align-items: center;
        padding: .375rem .75rem;
      }
      
      span.input-group-text-help {
        border: 1px solid #4c5a67;
        cursor: help;
      }
      input {
        border-left: 0px;
      }

    </style>
      <div class="input-group">
        <span class="input-group-prepend" id="`+this.elId+`_infoSpanSpan">
          <span 
            class="input-group-text input-group-text-help bg-dark b-1 text-secondary"
            id="`+this.elId+`_infoSpan"
            data-toggle="tooltip" 
            data-placement="bottom" 
            data-html="true" 
            title=""
            >
            <i class="fas fa-info-circle"></i>
          </span>
        </span>
        <span class="input-group-append" id="`+this.elId+`_clockSpanSpan">
          <span 
            class="input-group-text-icon form-control form-control-sm b-1 "
            title=""
            >
            <i class="far fa-clock text-muted"></i>
          </span>
        </span>

        <span id="`+this.elId+`_input_container" class="input-group-append" style="width: calc(100% - 44px);">
          <input 
            id="`+this.elId+`_timepicker" 
            class="form-control form-control-sm timepicker timepicker-with-dropdown"
            readonly="readonly"
          />
        </span>
        <span class="input-group-append">
          <button
            type="button" 
            id="`+this.elId+`_cancelButton"
            class="btn btn-sm pl-3 pr-3 waves-effect waves-light btn-secondary"
            style="display: none;"
            data-toggle="tooltip" 
            data-placement="bottom" 
            data-html="true" 
            title="<em>Annuleren</em>"
            >
            <i class="fas fa-times"></i>
          </button> 
          <button
            type="button" 
            id="`+this.elId+`_editApplyButton"
            class="btn btn-sm pl-3 pr-3 waves-effect waves-light btn-low-key-warning"
            data-toggle="tooltip" 
            data-placement="bottom" 
            data-html="true" 
            title="<em>Wijzigen</em>"
            >
            <i class="fas fa-lock"></i>
          </button> 
        </span>
      </div>`

    this.locked = true
    this.prevTime = '' // Contains the state before opening, to return to on cancel

    this._shadowRoot = this.attachShadow({ mode: 'open' })
    this._shadowRoot.appendChild(this.oppleo_edit_time_template.content.cloneNode(true))

    this.$input = this._shadowRoot.querySelector('input#'+this.elId+'_timepicker')
    this.$input_container = this._shadowRoot.querySelector('#'+this.elId+'_input_container')
    this.$info = this._shadowRoot.querySelector('span#'+this.elId+'_infoSpan')
    this.$infoSpan = this._shadowRoot.querySelector('span#'+this.elId+'_infoSpanSpan')
    this.$clock = this._shadowRoot.querySelector('span#'+this.elId+'_clockSpan')
    this.$clockSpan = this._shadowRoot.querySelector('span#'+this.elId+'_clockSpanSpan')
    this.$cancelButton = this._shadowRoot.querySelector('button#'+this.elId+'_cancelButton')
    this.$editApplyButton = this._shadowRoot.querySelector('button#'+this.elId+'_editApplyButton')

    // Prevent bubbling of the input click. It causes the timepicker dropdown to disappear immediately.
    this.$input.addEventListener('click', (ev) => {
      ev.stopPropagation()
    })


    this.$info.addEventListener('mouseenter', () => { 
      this.$info.classList.remove("bg-secondary")
      this.$info.classList.add("bg-success")
      this.$info.classList.remove("text-muted")
      this.$info.classList.add("text-light")
    })
    this.$info.addEventListener('mouseleave', () => { 
      this.$info.classList.remove("bg-success")
      this.$info.classList.add("bg-secondary")
      this.$info.classList.remove("text-light")
      this.$info.classList.add("text-muted")
    })

    this.$cancelButton.addEventListener('click', () => {

      // Cancelling, select the previous selected option
      this.locked = true
      this.options = this.prevOptions
      $(this.$input).timepicker('destroy').timepicker( this.options )

      this.render()

    })
    this.$editApplyButton.addEventListener('click', () => {

      if (this.locked) {
        // Unlock
        this.locked = false
        this.options = Object.assign(this.options, { dropdown: true })
        $(this.$input).timepicker('destroy').timepicker( this.options )

      } else {
        // Apply and lock
        this.locked = true
        this.options = Object.assign(this.options, { dropdown: false })
        let newValue = this.$input.value.split('u')[0]
        let oldValue = this.options.defaultTime
        this.options = Object.assign(this.options, { defaultTime: newValue })
        $(this.$input).timepicker('destroy').timepicker( this.options )

        this.prevOptions = this.options

        // Value actually changed?
        if (newValue !== oldValue) {
          this.dispatchEvent(
            new CustomEvent('apply', {
                bubbles: true, 
                detail: { 
                  newValue: newValue,
                  oldValue: oldValue
                }
            })
          )
        }
      }

      this.render()
    })

  }
  get id() {
    return this.getAttribute('id')
  }
  set id(value) {
    this.setAttribute('id', value)
  }
  get value() {
    return this.getAttribute('value')
  }
  set value(value) {
    this.setAttribute('value', value)
  }
  get info() {
    return this.getAttribute('info')
  }
  set info(value) {
    this.setAttribute('info', value)
  }

  // Timeticker options - json in string format in the attribute (can only hold strings)
  get options() {
    let defaultOptions = {
      timeFormat: 'HH:mmu',
      interval: 1,
      minTime: '0',
      maxTime: '23:59',
      defaultTime: '05:00',
      startTime: '00:00',
      dynamic: true,
      dropdown: ((!this.locked) || this.unlock),
      scrollbar: true
    }
    if (this.hasAttribute('options')) {
      // Combine settings in attribute with defaults
      return Object.assign(defaultOptions, JSON.parse(this.getAttribute('options')))
    }
    // else return default options
    return defaultOptions
  }
  // The options property should be an array of options.
  // Attributes can only contain a string, convert array to string when setting
  // Don't convert when the value is already a string
  set options(value) {
    if (typeof value !== "string") {
      this.setAttribute('options', JSON.stringify(value))
    } else {
      this.setAttribute('options', value)
    }
  }
  get unlock() {
    return (this.getAttribute('unlock') === 'true')
  }
  set unlock(value) {
    this.setAttribute('lock', value)
  }
  static get observedAttributes() {
    return ['options', 'info', 'unlock']
  }
  attributeChangedCallback(name, oldVal, newVal) {
    this.render()
  }
  connectedCallback() {

    $(this.$info).tooltip({ boundary: 'window' })
    $(this.$cancelButton).tooltip({ boundary: 'window' })
    $(this.$editApplyButton).tooltip({ boundary: 'window' })
    
    this.prevOptions = this.options
    $(this.$input).timepicker( this.options )
    
    this.render() // needed, doesn't call it by itself
  }
  render() {

    if (this.locked && !this.unlock) {
      // Lock
      this.$input.setAttribute('readonly', 'readonly')
      // Hide the info span
      this.$infoSpan.style.display = "none"
      this.$clockSpan.classList.add("input-group-append")
      this.$clockSpan.classList.remove("input-group-prepend")
      this.$clockSpan.style.display = "none"
      // Info span hidden, make the input container the prepend
      this.$input_container.classList.add("input-group-prepend")
      this.$input_container.classList.remove("input-group-append")
      this.$cancelButton.style.display = "none"
      this.$input_container.style.width = 'calc(100% - 44px)';
      this.$editApplyButton.setAttribute('data-original-title', '<em>Wijzigen</em>')
      this.$editApplyButton.innerHTML = '<i class="fas fa-lock"></i>'
      this.$editApplyButton.classList.add("btn-low-key-warning")
      this.$editApplyButton.classList.remove("btn-primary")    
    } else {
      // Not locked or unlock
      this.$input.removeAttribute('readonly')
      if (this.info != null) {
        this.$infoSpan.style.display = ""
      } else {
        this.$infoSpan.style.display = "none"
        this.$clockSpan.classList.add("input-group-prepend")
        this.$clockSpan.classList.remove("input-group-append")
        }
      this.$clockSpan.style.display = ""

      // Info span shown, make the input container the append
      this.$input_container.classList.remove("input-group-prepend")
      this.$input_container.classList.add("input-group-append")
      this.$cancelButton.style.display = ""
      this.$editApplyButton.setAttribute('data-original-title', '<em>Opslaan</em>')
      this.$editApplyButton.innerHTML = '<i class="far fa-save"></i>'
      this.$editApplyButton.classList.remove("btn-low-key-warning")
      this.$editApplyButton.classList.add("btn-primary")
      this.$editApplyButton.blur()
      if (this.info != null) {
        this.$input_container.style.width = 'calc(100% - 167px)' // 130/ 178
      } else {
        this.$input_container.style.width = 'calc(100% - 125px)' // 88/ 136
      }

      // If not locked, unlock and hide apply and cancel buttons
      if (this.unlock) {
        $(this.$cancelButton).hide()
        $(this.$editApplyButton).hide()
        if (this.info == null) {
          this.$input_container.style.width = 'calc(100% - 37px)' // 0px
        } else {
          this.$input_container.style.width = 'calc(100% - 79px)' // 42px
        }
      } else {
        $(this.$cancelButton).show()
        $(this.$editApplyButton).show()
      }

    }

    this.$info.setAttribute('data-original-title', this.info)

  }
}
window.customElements.define('oppleo-edit-time', OppleoEditTime)






