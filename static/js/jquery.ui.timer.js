(function($) {
    $.widget("ui.timer", {
        options: {
          initial_seconds: 0,
          hidden_selector: null,
          autostart: true
        },

        _create: function() {
            $(this.element).addClass("ui-timer");

            this.timeDisplayElement = document.createElement("div");
            $(this.timeDisplayElement).addClass("timer-display");

            $(this.element).append(this.timeDisplayElement);

            this._createButton();

            this.extraTime = this.options.initial_seconds * 1000;
            this.active = false;

            this.refresh();

            if (this.options["autostart"]) {
                this.start();
            }
        },

        refresh: function() {
            this._refreshTime();
            this._redrawTime();
        },

        toggle: function() {
            this[this.active ? "stop" : "start"]();
        },

        stop: function() {
            clearInterval(this.intervalId);
            this.extraTime += this._elapsedMillisecondsSinceStart();

            this.active = false;
            this._setButton();
        },

        start: function() {
            this.active = true;
            this._setButton();
            this.startTime = this._getCurrentTime();
            this.intervalId = setInterval($.proxy(function() {
                this.refresh();
            },this), 100);
        },

        seconds: function() {
            return this.milliseconds() / 1000.0;
        },

        milliseconds: function() {
            return this._elapsedMillisecondsSinceStart() + this.extraTime;
        },

        _elapsedMillisecondsSinceStart: function() {
            if (!this.active) { return 0; }

            var now = this._getCurrentTime();
            return now - this.startTime;
        },

        _refreshTime: function() {
            var displayTime = this.seconds();

            this.displayMinutes = Math.floor(displayTime / 60);
            this.displaySeconds = Math.floor(displayTime % 60);

            if (this.options["hidden_selector"]) {
                value = Math.floor(displayTime);
                el = $(this.options["hidden_selector"]);

                if (el.attr("value") != value) {
                    el.attr("value", value);
                }
            }
        },

        _redrawTime: function() {
            var timeText = this._padZero(this.displayMinutes);
            timeText += " : ";
            timeText += this._padZero(this.displaySeconds);

            $(this.timeDisplayElement).text(timeText);
        },

        _createButton: function() {
            this.buttonContainer = document.createElement("div");
            $(this.buttonContainer).addClass("pause-button-container");

            this.buttonElement = document.createElement("div");
            $(this.buttonElement).addClass("pause-button");

            $(this.element).append(this.buttonContainer);
            $(this.buttonContainer).append(this.buttonElement);

            this._setButton();

            $(this.buttonElement).click($.proxy(function() {
                this.toggle();
            },this));
        },

        _getButtonLabel: function() {
            return this.active ? "Pause" : "Resume";
        },

        _setButton: function() {
            $(this.buttonElement).button({ label: this._getButtonLabel() });
        },

        _padZero: function(number) {
            numberString = number + "";
            if (numberString.length == 1) {
                numberString = "0" + numberString;
            }
            return numberString;
        },

        _getCurrentTime: function () {
            return (new Date()).getTime();
        }

    });
})(jQuery);