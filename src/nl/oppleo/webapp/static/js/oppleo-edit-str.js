/* 
  Oppleo Edit String Web Component
*/

const template = document.createElement('template');

template.innerHTML = `
  <!-- App css -->
  <link rel="stylesheet" type="text/css" href="/static/css/bootstrap.min.css">
  <link rel="stylesheet" type="text/css" href="/static/css/icons.css">
  <link rel="stylesheet" type="text/css" href="/static/css/style.css">


  <script src="/static/js/bootstrap.min.js"></script>
  <script src="/static/js/waves.js"></script>
  <link rel="stylesheet" href="/static/plugins/bootstrap4-toggle/3.6.1/bootstrap4-toggle.min.css">
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
</style>
  <div class="input-group">
    <input 
      class="form-control input-sm" 
      type="text"
      readonly="readonly"
      style="text-align: left; width: flex;"
      placeholder=""
      value=""
    />
    <span class="input-group-btn">
      <button
        type="button" 
        class="btn btn-xs waves-effect waves-light btn-secondary"
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
        class="btn btn-xs waves-effect waves-light btn-low-key-warning"
        data-toggle="tooltip" 
        data-placement="bottom" 
        data-html="true" 
        title="<em>Wijzigen</em>"
        >
        <i class="fas fa-lock"></i>
      </button> 
    </span>
  </div>`

class OppleoEdit extends HTMLElement {
  constructor() {
    super()
    this._shadowRoot = this.attachShadow({ mode: 'open' })
    this._shadowRoot.appendChild(template.content.cloneNode(true))

    this.$input = this._shadowRoot.querySelector('input')
    this.$cancelButton = this._shadowRoot.querySelector('button:nth-child(1)')
    this.$editApplyButton = this._shadowRoot.querySelector('button:nth-child(2)')

    this.$cancelButton.addEventListener('click', () => {
      this.$input.value = this.prefix + this.$input.getAttribute('placeholder')
      this.$input.setAttribute('readonly', 'readonly')
      this.$cancelButton.style.display = "none"
      this.$editApplyButton.setAttribute('data-original-title', 'Wijzigen')
      //        $('#editbutton_' + id + '_editsave').tooltip('hide')
      this.$editApplyButton.innerHTML = '<i class="fas fa-lock"></i>'
      this.$editApplyButton.classList.add("btn-low-key-warning")
      this.$editApplyButton.classList.remove("btn-primary")      
    })
    this.$editApplyButton.addEventListener('click', () => {
      if (this.$editApplyButton.innerHTML.indexOf("fa-lock") >= 0) {
        // Unlock
        this.$input.value =
          this.$input.value.replace(this.prefix, '')
        this.$input.setAttribute('placeholder', this.$input.value)
        this.$input.removeAttribute('readonly')
        this.$cancelButton.style.display = ""
        this.$editApplyButton.setAttribute('data-original-title', 'Opslaan')
//        $('#editbutton_' + id + '_editsave').tooltip('hide')
        this.$editApplyButton.innerHTML = '<i class="far fa-save"></i>'
        this.$editApplyButton.classList.remove("btn-low-key-warning")
        this.$editApplyButton.classList.add("btn-primary")
      } else {
        // Save
        this.$input.setAttribute('placeholder', this.$input.value)
        this.$input.value = this.prefix + this.$input.value
        this.$input.setAttribute('readonly', 'readonly')
        this.$cancelButton.style.display = "none"
        this.$editApplyButton.setAttribute('data-original-title', 'Wijzigen')
//        $('#editbutton_' + id + '_editsave').tooltip('hide')
        this.$editApplyButton.innerHTML = '<i class="fas fa-lock"></i>'
        this.$editApplyButton.classList.add("btn-low-key-warning")
        this.$editApplyButton.classList.remove("btn-primary")

        // TODO - save it - callback

      }      
    })

  }
  get prefix() {
    return this.getAttribute('prefix')
  }
  set prefix(value) {
    this.setAttribute('prefix', value)
  }
  get value() {
    return this.getAttribute('value')
  }
  set value(value) {
    this.setAttribute('value', value)
  }
  static get observedAttributes() {
    return ['prefix', 'value']
  }
  attributeChangedCallback(name, oldVal, newVal) {
    this.render()
  }
  connectedCallback() {
    this.$input.value = this.prefix + this.value
    $(this.$cancelButton).tooltip({ boundary: 'window' })
    $(this.$editApplyButton).tooltip({ boundary: 'window' })
  }
  render() {
  }
}
window.customElements.define('oppleo-edit-str', OppleoEdit)






