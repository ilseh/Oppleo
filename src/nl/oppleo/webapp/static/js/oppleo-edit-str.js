/* 
  Oppleo Edit String Web Component
*/

const oppleo_edit_str_template = document.createElement('template');

oppleo_edit_str_template.innerHTML = `
  <!-- App css -->
  <link rel="stylesheet" type="text/css" href="/static/plugins/bootstrap/4.4.1/css/bootstrap.min.css">
  <link rel="stylesheet" type="text/css" href="/static/css/icons.css">
  <link rel="stylesheet" type="text/css" href="/static/css/style.css">
  <script src="/static/plugins/bootstrap/4.4.1/js/bootstrap.min.js"></script>
  <script src="/static/js/waves.js"></script>
  <link rel="stylesheet" type="text/css" href="/static/plugins/fontawesome/5.12.0/css/all.css">
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
    <span class="input-group-prepend">
      <span 
        class="input-group-text bg-dark b-1 text-secondary"
        style="display: none;"
        data-toggle="tooltip" 
        data-placement="bottom" 
        data-html="true" 
        title=""
        >
        <i class="fas fa-info-circle"></i>
      </span>
    </span>
    <input 
      class="form-control form-control-sm" 
      type="text"
      readonly="readonly"
      style="text-align: left; width: flex;"
      placeholder=""
      value=""
    />
    <span class="input-group-append">
      <button
        type="button" 
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
    this.$info = this._shadowRoot.querySelector('span.input-group-text')
    this.$cancelButton = this._shadowRoot.querySelector('button:nth-child(1)')
    this.$editApplyButton = this._shadowRoot.querySelector('button:nth-child(2)')
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

    this.$cancelButton.addEventListener('click', () => {
      this.$input.value = this.prefix + this.$input.getAttribute('placeholder') + this.suffix
      this.$input.setAttribute('readonly', 'readonly')
      this.$info.style.display = "none"
      this.$cancelButton.style.display = "none"
      this.$editApplyButton.setAttribute('data-original-title', '<em>Wijzigen</em>')
      this.$editApplyButton.innerHTML = '<i class="fas fa-lock"></i>'
      this.$editApplyButton.classList.add("btn-low-key-warning")
      this.$editApplyButton.classList.remove("btn-primary")    
      this.drawValidationBorder()  
    })
    this.$editApplyButton.addEventListener('click', () => {
      if (this.$editApplyButton.innerHTML.indexOf("fa-lock") >= 0) {
        // Unlock
        this.$input.value =
          this.$input.value.replace(this.prefix, '').replace(this.suffix, '')
        this.$input.setAttribute('placeholder', this.$input.value)
        this.$input.removeAttribute('readonly')
        if (this.info != null) this.$info.style.display = ""
        this.$cancelButton.style.display = ""
        this.$editApplyButton.setAttribute('data-original-title', '<em>Opslaan</em>')
        this.$editApplyButton.innerHTML = '<i class="far fa-save"></i>'
        this.$editApplyButton.classList.remove("btn-low-key-warning")
        this.$editApplyButton.classList.add("btn-primary")
        this.$editApplyButton.blur()
      } else {
        // Apply - validate first
        let newValue = this.$input.value
        let oldValue = this.$input.getAttribute('placeholder')
        // Only if valid
        if (this.validate(newValue)) {
          this.$input.setAttribute('placeholder', newValue)
          this.$input.value = this.prefix + newValue + this.suffix
          this.$input.setAttribute('readonly', 'readonly')
          this.$info.style.display = "none"
          this.$cancelButton.style.display = "none"
          this.$editApplyButton.setAttribute('data-original-title', '<em>Wijzigen</em>')
          this.$editApplyButton.innerHTML = '<i class="fas fa-lock"></i>'
          this.$editApplyButton.classList.add("btn-low-key-warning")
          this.$editApplyButton.classList.remove("btn-primary")

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
  static get observedAttributes() {
    return ['prefix', 'value', 'suffix', 'info']
  }
  attributeChangedCallback(name, oldVal, newVal) {
    this.render()
  }
  connectedCallback() {
    this.$input.value = this.prefix + this.value + this.suffix
    $(this.$info).tooltip({ boundary: 'window' })
    $(this.$cancelButton).tooltip({ boundary: 'window' })
    $(this.$editApplyButton).tooltip({ boundary: 'window' })
  }
  drawValidationBorder() {
    if (this.validate(this.$input.value)) {  // Valid
      this.$input.classList.remove("border", "border-danger")
    } else {                                // Invalid
      this.$input.classList.add("border", "border-danger")
    }
  }
  validate(newValue) {
    // If Locked valid by definition
    if (this.$editApplyButton.innerHTML.indexOf("fa-lock") >= 0) { return true }
    if (this.$regex == undefined) { this.$regex = new RegExp(this.validation) }
    return (this.validation == "" || this.$regex.test(newValue)) 
  }
  render() {
    this.$info.setAttribute('data-original-title', this.info)
  }
}
window.customElements.define('oppleo-edit-str', OppleoEditStr)






