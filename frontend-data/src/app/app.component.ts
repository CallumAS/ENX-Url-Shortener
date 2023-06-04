import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],

})

export class AppComponent {
  title = 'link-shortener';
  //inputs
  token: string = '';
  link: string = '';
  //stored items
  message: string = '';

  shortened = JSON.parse(localStorage.getItem('shortened') || '[]');

  constructor(private http: HttpClient) { }

  onLinkChange(event: Event) {
    this.link = (event.target as HTMLInputElement).value;
  }

  onVerify(token: string) {
    // The verification process was successful.
    // You can verify the token on your server now.
    this.token = token;
  }

  onExpired(response: any) {
    // The verification expired.
  }

  onError(error: any) {
    // An error occured during the verification process.
  }
  getDomain() {
    var protocol = window.location.protocol;
    var hostname = window.location.hostname;
    var port = window.location.port;

    return (protocol === "https:" ? "https://" : "http://") + hostname + (port ? ":" + port : "");
  }

  sendPostRequest() {
    const url = this.getDomain() + '/shorten'; // Replace with your API endpoint URL
    const data = { link: this.link, token: this.token }; // Replace with the data you want to send

    this.http.post(url, data)
      .subscribe(
        (response: any) => {
          // Handle the response from the server
          if (response.status === true) {
            this.shortened.push({ link: response.link, shortened: response.shortened })
            localStorage.setItem('shortened', JSON.stringify(this.shortened));
          } else {
            this.message = response.message;
            setTimeout(() => {
              this.message = "";
            }, 5000);
          }

          console.log('Post request successful', JSON.stringify(this.shortened));
        },
        error => {
          // Handle any errors that occurred
          console.error('An error occurred:', error);
        }

      );

    //dirty trick to refresh captcha 
    var element = document.querySelector("app-root ng-hcaptcha");
    if (element) {
      var clonedElement = element.cloneNode(true);

      element.parentNode?.replaceChild(clonedElement, element);
    }
  }
}