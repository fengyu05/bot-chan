from fluctlight.agents.expert.data_model import IntakeMessage, TaskConfig, TaskEntity
from fluctlight.agents.expert.task_agent import TaskAgent
from fluctlight.intent.message_intent import create_intent

INTENT_KEY = "SHOPPING_ASSIST"


class ProductSpec(TaskEntity):
    name: str
    choices: list[str]

    @property
    def desc_short(self) -> str:
        return f'{self.name}:[{" ".join(self.choices)}]'


class Product(TaskEntity):
    id: str
    name: str
    description: str
    price: float
    specs: list[ProductSpec]

    @property
    def desc_short(self) -> str:
        return f"id: {self.name} name: {self.name}, desc: {self.description}, price: {self.price}"

    @property
    def all_spec(self) -> str:
        return " ".join([spec.desc_short for spec in self.specs])


class ProductMatch(TaskEntity):
    match: bool
    product: Product


class Order(TaskEntity):
    product_id: str
    quantity: str
    spec: ProductSpec


class Inventory(TaskEntity):
    products: dict[str, Product]

    @property
    def all_product_desc(self) -> str:
        return " ".join([p.product_desc_short for p in self.products.values()])


def create_inventory() -> Inventory:
    return Inventory(
        products={
            "shoe_001": Product(
                id="shoe_001",
                name="Asics running shoe GLIDERIDE MAX",
                description="The GLIDERIDE® MAX shoe is the long-run cruiser that makes your training feel smoother and more consistent.",
                price=240.0,
                specs=[
                    ProductSpec(
                        name="size", choices=["size_6", "size_7", "size_8", "size_9"]
                    )
                ],
            )
        }
    )


def create_shopping_assisist_task_agent() -> TaskAgent:
    return TaskAgent(
        name="Shopping assisist",
        description="This task assisist shopper to discover what product are avialiable, place order and follow the status of the order.",
        intent=create_intent(INTENT_KEY),
        context={"inventory": create_inventory()},
        task_graph=[
            TaskConfig(
                task_key="product_interests",
                instruction="Take users input, match with the below inventors. User input: {message.text} \n Inventory: {inventory.all_product_desc} ",
                input_schema={"message": IntakeMessage},
                output_schema=ProductMatch,
                loop_message="Please select from the following inventory: {inventory.all_product_desc}",
                success_criteria=lambda x: x.match == True,
            ),
            TaskConfig(
                task_key="product_specs",
                instruction="You seems to be interested in {product_interests.product.desc_short}. \n The product has specs {product_interests.product.all_specs}. How do you want your order.",
                input_schema={
                    "message": IntakeMessage,
                    "product_interests": ProductMatch,
                },
                output_schema=Order,
            ),
        ],
    )
