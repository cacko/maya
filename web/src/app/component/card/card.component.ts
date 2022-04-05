import { Component, Input } from "@angular/core";
import { Image } from "../../entity/image";
import { Router } from "@angular/router";

@Component({
  selector: "app-card",
  templateUrl: "./card.component.html",
  styleUrls: ["./card.component.scss"]
})
export class CardComponent {

  @Input() image?: Image;

  constructor(private router: Router) {
  }

  style(): { [key: string]: string } {
    return {
      "background-image": `url("${this.image?.thumb}")`,
      "background-size": "cover"
    };
  }

  onClick() {
    this.router.navigate(["full-view", this.image?.id], { preserveFragment: true });
  }

}
