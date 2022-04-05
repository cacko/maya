import { NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";
import { AppRoutingModule } from "./app-routing.module";
import { AppComponent } from "./app.component";
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import { initializeApp, provideFirebaseApp } from "@angular/fire/app";
import { environment } from "../environments/environment";
import { getAuth, provideAuth } from "@angular/fire/auth";
import { AuthService } from "./service/auth.service";
import { PhotosService } from "./service/photos.service";
import { SETTINGS as AUTH_SETTINGS } from "@angular/fire/compat/auth";
import { AngularFireModule } from "@angular/fire/compat";
import { CardComponent } from "./component/card/card.component";
import { HttpClientModule } from "@angular/common/http";
import { InfiniteScrollModule } from "ngx-infinite-scroll";
import { ServiceWorkerModule } from "@angular/service-worker";
import { LoaderComponent } from "./component/loader/loader.component";
import { MatProgressBarModule } from "@angular/material/progress-bar";
import { MatSnackBarModule } from "@angular/material/snack-bar";
import { MatRippleModule } from "@angular/material/core";
import { MatButtonModule } from "@angular/material/button";
import { FullViewComponent } from "./component/full-view/full-view.component";
import { MatIconModule } from "@angular/material/icon";


const MATERIALS = [
  MatProgressBarModule,
  MatSnackBarModule,
  MatRippleModule,
  MatButtonModule,
  MatIconModule
];

@NgModule({
  declarations: [
    AppComponent,
    CardComponent,
    LoaderComponent,
    FullViewComponent
  ],
  imports: [
    BrowserModule,
    InfiniteScrollModule,
    ...MATERIALS,
    AppRoutingModule,
    HttpClientModule,
    BrowserAnimationsModule,
    AngularFireModule.initializeApp(environment.firebase),
    provideFirebaseApp(() => initializeApp(environment.firebase)),
    provideAuth(() => getAuth()),
    ServiceWorkerModule.register("ngsw-worker.js", {
      enabled: environment.production,
      // Register the ServiceWorker as soon as the application is stable
      // or after 30 seconds (whichever comes first).
      registrationStrategy: "registerWhenStable:30000"
    })
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
