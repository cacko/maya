import { Component, Input } from "@angular/core";
import { Image } from "../../entity/image";

@Component({
  selector: "app-card",
  templateUrl: "./card.component.html",
  styleUrls: ["./card.component.scss"]
})
export class CardComponent {

  @Input() image?: Image;

  constructor() {
  }

  style(): { [key: string]: string } {
    return {
      "background-image": `url("${this.image?.thumb}")`,
      "background-size": "cover"
    };
  }

}
