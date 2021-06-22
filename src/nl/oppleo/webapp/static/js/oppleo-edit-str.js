/* 
  Oppleo Edit String Web Component


  Options:
    - hide='************' shoes the string when locked. Useful for passwords.

     <i class="far fa-eye"></i>
     <i class="far fa-eye-slash"></i>
*/

const oppleo_edit_str_template = document.createElement('template');

oppleo_edit_str_template.innerHTML = `
  <!-- App css -->
  <link rel="stylesheet" type="text/css" href="/static/plugins/bootstrap/4.4.1/css/bootstrap.min.css">
  <link rel="stylesheet" type="text/css" href="/static/css/icons.css">
  <link rel="stylesheet" type="text/css" href="/static/css/style.css">

  <script src="/static/js/jquery-3.3.1.js"></script>
  
  <script src="/static/plugins/bootstrap/4.4.1/js/bootstrap.min.js"></script>
  <script src="/static/js/waves.js"></script>

  <!-- Fontawesome -->
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
  span.input-group-text {
    cursor: help;
    border: 1px solid #4c5a67;
  }
</style>
  <div class="input-group">
    <span class="input-group-prepend" id="infoSpanSpan">
      <span 
        class="input-group-text bg-dark b-1 text-secondary"
        id="infoSpan"
        data-toggle="tooltip" 
        data-placement="bottom" 
        data-html="true" 
        title=""
        >
        <i class="fas fa-info-circle"></i>
      </span>
    </span>
    <span id="input_container" class="input-group-append" style="width: calc(100% - 44px);">
      <input 
        class="form-control form-control-sm" 
        type="text"
        readonly="readonly"
        style="text-align: left; width: flex;"
        placeholder=""
        value=""
      />
    </span>
    <span class="input-group-append">
      <button
        type="button" 
        id="hideEditButton"
        class="btn btn-sm pl-2 pr-2 waves-effect waves-light btn-outline-success"
        style="display: none;"
        data-toggle="tooltip" 
        data-placement="bottom" 
        data-html="true" 
        title="<em>Toon</em>"
        >
        <i class="far fa-eye"></i>
      </button>
      <button
        type="button" 
        id="cancelButton"
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
        id="editApplyButton"
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

class OppleoEditStr extends HTMLElement {
  constructor() {
    super()
    this._shadowRoot = this.attachShadow({ mode: 'open' })
    this._shadowRoot.appendChild(oppleo_edit_str_template.content.cloneNode(true))

    this.$input = this._shadowRoot.querySelector('input')
    this.$input_container = this._shadowRoot.querySelector('#input_container')
    this.$info = this._shadowRoot.querySelector('span#infoSpan')
    this.$infoSpan = this._shadowRoot.querySelector('span#infoSpanSpan')
    this.$hideEditButton = this._shadowRoot.querySelector('button#hideEditButton')
    this.$cancelButton = this._shadowRoot.querySelector('button#cancelButton')
    this.$editApplyButton = this._shadowRoot.querySelector('button#editApplyButton')
    this.$regex = undefined

    this.$input.addEventListener('keypress', () => { this.drawValidationBorder() })
    this.$input.addEventListener('paste', () => { this.drawValidationBorder() })
    this.$input.addEventListener('input', () => { this.drawValidationBorder() })

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

    this.$hideEditButton.addEventListener('click', () => {
      if (this.$input.getAttribute('type') == "text") {
        // hide: text --> password
        this.$input.setAttribute('type', 'password')
        this.$hideEditButton.setAttribute('data-original-title', '<em>Toon</em>')
        this.$hideEditButton.innerHTML = '<i class="far fa-eye"></i>'
      } else {
        // show: password --> text
        this.$input.setAttribute('type', 'text')
        this.$hideEditButton.setAttribute('data-original-title', '<em>Verberg</em>')
        this.$hideEditButton.innerHTML = '<i class="far fa-eye-slash"></i>'
      }      
      $(this.$hideEditButton).tooltip('hide')  // Make sure tooltips don't remain
      this.$hideEditButton.blur()
    })

    this.$cancelButton.addEventListener('click', () => {
      if (this.hide != undefined) {
        this.$input.value = this.hide
        this.$input.setAttribute('type', 'text')
      } else {
        if (this.hideEdit != undefined) {
          this.$input.setAttribute('type', 'password')
        } else {
          this.$input.value = this.prefix + this.$input.getAttribute('placeholder') + this.suffix        
        }
      }
      this.$input.setAttribute('readonly', 'readonly')
      //this.$info.style.display = "none"
      // Hide the info span
      this.$infoSpan.style.display = "none"
      // Info span hidden, make the input container the prepend
      this.$input_container.classList.add("input-group-prepend")
      this.$input_container.classList.remove("input-group-append")

      this.$cancelButton.style.display = "none"
      this.$input_container.style.width = 'calc(100% - 44px)';
      this.$editApplyButton.setAttribute('data-original-title', '<em>Wijzigen</em>')
      this.$editApplyButton.innerHTML = '<i class="fas fa-lock"></i>'
      this.$editApplyButton.classList.add("btn-low-key-warning")
      this.$editApplyButton.classList.remove("btn-primary")    
      // Hide the hide/show button in locked view
      this.$hideEditButton.style.display = "none"
      this.drawValidationBorder()  
    })
    this.$editApplyButton.addEventListener('click', () => {
      if (this.$editApplyButton.innerHTML.indexOf("fa-lock") >= 0) {
        // Unlock
        if (this.hideEdit != undefined) {
          this.$input.setAttribute('type', 'password')
        }
        if (this.hide != undefined) {
          this.$input.value = this.value
        }
        this.$input.value =
          this.$input.value.replace(this.prefix, '').replace(this.suffix, '')
        this.$input.setAttribute('placeholder', this.$input.value)
        this.$input.removeAttribute('readonly')
        // if (this.info != null) this.$info.style.display = ""
        if (this.info != null) this.$infoSpan.style.display = ""
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
          if (this.hideEdit != null) {
            this.$input_container.style.width = 'calc(100% - 164px)'; // 130 + 34
          } else {
            this.$input_container.style.width = 'calc(100% - 130px)'; // 130
          }
        } else {
          if (this.hideEdit != null) {
            this.$input_container.style.width = 'calc(100% - 122px)'; // 88 + 34
          } else {
            this.$input_container.style.width = 'calc(100% - 88px)'; // 88
          }
        }
        // Password view
        if (this.hideEdit != undefined) {
          // Show the hide/show button in edit view
          this.$hideEditButton.style.display = ""
        }
      } else {
        // Apply - validate first
        let newValue = this.$input.value
        let oldValue = this.$input.getAttribute('placeholder')
        // Only if valid
        if (this.validate(newValue)) {
          this.$input.setAttribute('placeholder', newValue)
          if (this.hide != undefined) {
            this.$input.value = this.hide
          } else {
            this.$input.value = this.prefix + newValue + this.suffix        
          }
          this.$input.setAttribute('readonly', 'readonly')
          //this.$info.style.display = "none"
          this.$infoSpan.style.display = "none"
          // Info span hidden, make the input container the append
          this.$input_container.classList.add("input-group-prepend")
          this.$input_container.classList.remove("input-group-append")

          this.$cancelButton.style.display = "none"
          this.$editApplyButton.setAttribute('data-original-title', '<em>Wijzigen</em>')
          this.$editApplyButton.innerHTML = '<i class="fas fa-lock"></i>'
          this.$editApplyButton.classList.add("btn-low-key-warning")
          this.$editApplyButton.classList.remove("btn-primary")
          this.$input_container.style.width = 'calc(100% - 44px)';
          // Hide the hide/show button in locked view
          this.$hideEditButton.style.display = "none"

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
          this.$editApplyButton.blur()
        }
      }
    })

  }
  get id() {
    return this.getAttribute('id')
  }
  set id(value) {
    this.setAttribute('id', value)
  }
  get prefix() {
    let p = this.getAttribute('prefix')
    return ( typeof p === 'string' ? p : "" )
  }
  set prefix(value) {
    this.setAttribute('prefix', value)
  }
  get suffix() {
    let p = this.getAttribute('suffix')
    return ( typeof p === 'string' ? p : "" )
  }
  set suffix(value) {
    this.setAttribute('suffix', value)
  }
  get value() {
    return this.getAttribute('value')
  }
  set value(value) {
    this.setAttribute('value', value)
    this.$input.value = value  
    this.drawValidationBorder()
  }
  get validation() {
    return this.getAttribute('validation')
  }
  set validation(value) {
    this.setAttribute('validation', value)
  }
  get info() {
    return this.getAttribute('info')
  }
  set info(value) {
    this.setAttribute('info', value)
  }
  get hide() {
    return this.getAttribute('hide')
  }
  set hide(value) {
    this.setAttribute('hide', value)
  }
  get hideEdit() {
    return this.getAttribute('hideEdit')
  }
  set hideEdit(value) {
    this.setAttribute('hideEdit', value)
  }
  get unlock() {
    return (this.getAttribute('unlock') === 'true')
  }
  set unlock(value) {
    this.setAttribute('lock', value)
  }
  static get observedAttributes() {
    return ['prefix', 'value', 'suffix', 'info']
  }
  attributeChangedCallback(name, oldVal, newVal) {
    this.render()
  }
  connectedCallback() {
    if (this.hide != undefined) {
      this.$input.value = this.hide
      this.$input.setAttribute('type', 'text')
    } else {
      if (this.hideEdit != undefined) {
        this.$input.setAttribute('type', 'password')
      } else {
        this.$input.value = this.prefix + this.value + this.suffix
      }
    }
    $(this.$info).tooltip({ boundary: 'window' })
    $(this.$hideEditButton).tooltip({ boundary: 'window' })
    $(this.$cancelButton).tooltip({ boundary: 'window' })
    $(this.$editApplyButton).tooltip({ boundary: 'window' })
    // If not locked, unlock and hide apply and cancel buttons
    if (this.unlock) {
      this.$editApplyButton.click()
      $(this.$editApplyButton).hide()
      $(this.$cancelButton).hide()
      if (this.info == null) {
        if (this.hideEdit != null) {
          $(this.$input_container).css('width', 'calc(100% - 34px)')   // 0 + 34
        } else {
          $(this.$input_container).css('width', 'calc(100% - 0px)')   // 0
        }
        // Unlocked, but no info. Hide the info button
        this.$infoSpan.style.display = "none"
        // Info span hidden, make the input container the prepend
        this.$input_container.classList.add("input-group-prepend")
        this.$input_container.classList.remove("input-group-append")
      } else {
        if (this.hideEdit != null) {
          $(this.$input_container).css('width', 'calc(100% - 76px)')  // 42 + 34
        } else {
          $(this.$input_container).css('width', 'calc(100% - 42px)')  // 42
        }
      }
    } else {
      // Locked, hide the info button
      this.$infoSpan.style.display = "none"
      // Info span hidden, make the input container the prepend
      this.$input_container.classList.add("input-group-prepend")
      this.$input_container.classList.remove("input-group-append")
    }
  }
  drawValidationBorder() {
    if (this.validate(this.$input.value)) {   // Valid
      this.$input.classList.remove("border", "border-danger")
    } else {                                  // Invalid
      this.$input.classList.add("border", "border-danger")
    }
    this.dispatchEvent(
      new CustomEvent('change', {
          bubbles: true, 
          detail: { 
            value: this.$input.value,
            target: this.$input
          }
      })
    )
  }
  validate(newValue) {
    // If Locked valid by definition
    if (this.$editApplyButton.innerHTML.indexOf("fa-lock") >= 0) { return true }
    if (this.$regex == undefined) { this.$regex = new RegExp(this.validation) }
    return (this.validation == "" || this.$regex.test(newValue)) 
  }
  valid() {
    return this.validate(this.$input.value) 
  }
  render() {
    this.$info.setAttribute('data-original-title', this.info)
  }
}
window.customElements.define('oppleo-edit-str', OppleoEditStr)
