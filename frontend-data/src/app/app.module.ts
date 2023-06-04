import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';

import { NgHcaptchaModule } from 'ng-hcaptcha';

import { HttpClientModule } from '@angular/common/http';

@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    NgHcaptchaModule.forRoot({
      siteKey: 'a57a0df5-638c-4aae-8fc3-19b37b345c8a',
    }),
    HttpClientModule
  ],
  providers: [],
  bootstrap: [AppComponent],

})
export class AppModule { }
