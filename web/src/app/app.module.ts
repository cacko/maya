import { NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";
import { AppRoutingModule } from "./app-routing.module";
import { AppComponent } from "./app.component";
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import { initializeApp, provideFirebaseApp } from "@angular/fire/app";
import { environment } from "../environments/environment";
import { provideAuth, getAuth } from "@angular/fire/auth";
import { AuthService } from "./service/auth.service";
import { PhotosService } from "./service/photos.service";
import { SETTINGS as AUTH_SETTINGS } from "@angular/fire/compat/auth";
import { AngularFireModule } from "@angular/fire/compat";
import { CardComponent } from "./component/card/card.component";
import { ScrollingModule } from "@angular/cdk/scrolling";

@NgModule({
  declarations: [
    AppComponent,
    CardComponent
  ],
  imports: [
    BrowserModule,
    ScrollingModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    AngularFireModule.initializeApp(environment.firebase),
    provideFirebaseApp(() => initializeApp(environment.firebase)),
    provideAuth(() => getAuth())
  ],
  providers: [
    {
      provide: AUTH_SETTINGS,
      useValue: { appVerificationDisabledForTesting: true }
    },
    AuthService,
    PhotosService
  ],
  bootstrap: [AppComponent]
})
export class AppModule {
}
