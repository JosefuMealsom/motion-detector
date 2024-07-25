export class RangeInput {
  constructor(inputId, labelId, baseValue) {
    this.input = document.getElementById(inputId);
    this.label = document.getElementById(labelId);

    if (baseValue) {
      this.input.value = baseValue;
    }

    this.label.textContent = this.input.value;
    this.addEvents();
  }

  addEvents() {
    this.input.addEventListener("input", (evt) => {
      this.label.textContent = evt.target.value;
      if (this.updateCallback) {
        this.updateCallback(evt.target.value);
      }
    });

    this.input.addEventListener("change", (evt) => {
      if (this.updateCallback) {
        this.updateCallback(evt.target.value);
      }
    });
  }

  onChange(updateCallback) {
    this.updateCallback = updateCallback;
  }

  getValue() {
    return Number(this.input.value);
  }
}
