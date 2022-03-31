const TweetNlp = {
    data() {
      return {
        title: 'Disaster Tweet NLP',
        newtweet: '',
        oldtweet: '',
        disaster: null,
        pred: 0.0
      }
    },
    methods: {
        tweet() {
            this.oldtweet = this.newtweet.slice();
            const requestOptions = {
                method: "POST",
                body: JSON.stringify({v: "redacted", twit: this.oldtweet})
            };
            console.log(requestOptions);
            fetch("https://us-central1-constant-rig-331503.cloudfunctions.net/twitter-disaster", requestOptions)
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                  const error = (data) || response.status;
                  return Promise.reject(error);
                }
                this.pred = data[0];
                console.log(data);
            }).then(() => {
                if(this.pred > 0){
                    this.disaster = true;
                } 
                else if(this.pred <= 0) {
                    this.disaster = false;
                } //else null?
                this.$forceUpdate()
            }).catch(error => {
                console.error('There was an error!',error);
            });
        }
    }
  }
  
Vue.createApp(TweetNlp).mount('#app');
