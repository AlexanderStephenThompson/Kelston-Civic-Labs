# Supply Chain & Logistics — Reference Notes

> A refresher on supply chain management (SCM), organized around the journey of a unit of
> inventory: **Get** the raw materials, **Make** them into product, and **Move** it all
> (logistics). Company- and tool-specific names from the original notes have been generalized
> (e.g. "our ERP system", "the broker's TMS") so the concepts stand on their own.

## Table of Contents

- [Overview](#overview)
- [Get](#get) — *acquire raw materials / inputs*
  - [Procurement flow](#procurement-flow)
  - [Procurement planning](#procurement-planning)
- [Make](#make) — *manufacture*
  - [Production planning](#production-planning)
  - [Produce](#produce)
  - [Quality](#quality)
  - [Package](#package)
- [Move](#move) — *store, ship, receive, return (all logistics)*
  - [Logistics players](#logistics-players)
  - [Branches & facilities](#branches--facilities)
  - [Buying transportation](#buying-transportation)
  - [Outbound flow](#outbound-flow)
  - [Transportation reference](#transportation-reference)
  - [Receiving (inbound)](#receiving-inbound)
  - [Demand planning](#demand-planning)
  - [Storing & inventory](#storing--inventory)
  - [Systems](#systems)
  - [Returns (reverse logistics)](#returns-reverse-logistics)
- [Glossary & Quick Reference](#glossary--quick-reference)

## Overview

**Supply Chain Management (SCM)** is the work of coordinating a complex network of people,
processes, and technologies that all work together to deliver something of value to
customers. The goal is to anticipate what customers will need — by forecasting future
demand — so that goods are provided in the right quantities, at the right place and time,
and at a profit.

It depends on collaboration and communication across departments and partners, which
requires seamless coordination and transparency throughout the network. A good approach
weighs both up-front and ongoing costs — the **total cost of ownership** — to deliver value
holistically. In short: understand the demand for your goods, build a comprehensive
strategy, and then orchestrate allocation and inventory to match.

These notes group the whole field into three verbs — the journey of materials from raw input
to delivered product:

```
        GET                      MAKE                       MOVE
   raw materials in         turn inputs into          all the logistics
                            finished product
 +-----------------+      +-----------------+      +-------------------------+
 | source &        | ---> | manufacture,    | ---> | store, ship, receive,   |
 | receive inputs  |      | quality, pack   |      | return + buy freight    |
 | (procurement)   |      |                 |      | (transport, warehousing)|
 +-----------------+      +-----------------+      +-------------------------+
```

> **In a distribution business** the **Make** step is thin or absent — you **Get** finished
> goods from manufacturers and **Move** them onward. The manufacturing is your supplier's
> step, upstream of you. Zoom out and the cycle repeats at every link: each company gets,
> (maybe) makes, and moves to the next one down the line. (Most of these notes live in
> **Move** — logistics is where the day-to-day work is.)

**The channel — who's who in the chain.** Goods pass through a series of players on the way
from raw material to the final customer:

- **Manufacturer / Supplier** — uses raw materials to create products. Relative to us, these
  are the suppliers who send finished products to the distribution group, which then
  distributes them to its own customers.
- **Distributor** — buys products or product lines from manufacturers, typically warehouses
  them, and sells to wholesalers. Has the widest range of transportation modes available.
- **Wholesaler** — buys in bulk for intermediary distribution and sells to retailers, not to
  end customers directly.
- **Retailer** — the end of the channel; sells to the final customer.

(The transportation-specific players — shipper, carrier, fleet, broker — appear under
[Move](#move).)

---

# Get

*Acquire raw materials / inputs.* This is where inventory comes in the door — the raw materials
and purchased goods that feed production (or, for a distributor, the finished goods you resell).
At heart, procurement is **converting cash into inventory**: the strategic groundwork — vetting,
negotiating, and contracting (**Screen** and **Select**) — comes first; **Purchase** is the
execution (ordering and payment). End to end, that's the **Procure-to-Pay (P2P)** cycle. (Buying
the *transportation* to move goods is itself a kind of procurement, but these notes file it
under [Move](#move) with the rest of logistics.)

## Procurement flow

Three stages — Screen → Select → Purchase:

- **Screen** — identify the need and write detailed specs (a **requisition**), then gather
  information and shortlist suppliers using procurement documents (**RFI** = Request for
  Information, **RFP** = Request for Proposals). Supplier *screening* narrows the field;
  supplier *selection* picks the winner on certifications, scorecards, and bids. Usually you
  choose from a list of pre-approved vendors; if none fit, the RFP opens it to bids.
- **Select** — lock in the supplier and set the **arrangement**:
  - **Negotiated contract** — agreed terms locked in for ongoing supply (usually cheaper and
    more reliable).
  - **Spot buy / spot quote** — a non-contractual, one-off purchase at current market rates
    (often higher), for immediate needs. Use **quoting** to estimate cost first.

  Selection sits inside a set of ongoing procurement disciplines:
  - **Supplier & carrier negotiations** — regularly negotiate to secure favorable terms,
    improve service levels, and reduce costs.
  - **Supplier management** — build and maintain supplier relationships for reliable supply
    and quality of materials.
  - **Strategic sourcing** — identify, evaluate, and contract with suppliers to acquire the
    best goods and services.
  - **Contract management** — manage the resulting contracts so suppliers adhere to terms,
    conditions, and pricing.
  - **Supplier development** — teach suppliers what they need to know about your business and
    what you offer; can extend to process improvement, R&D, faster payments, business loans,
    or partnerships.
- **Purchase** — execute and track the buy. Send the chosen vendor a **Purchase Order (PO)**
  (quantities, items, pricing, delivery timelines, payment terms), which formalizes the deal
  and kicks off fulfillment. After checking inventory to confirm it can reliably fulfill, the
  vendor issues a **Sales Order (SO)** as confirmation. (Those SOs may then be sent to the
  ERP's shipment workbench to be dispatched.) Then **order placement → order tracking →
  payment processing**.

## Procurement planning

Planning applies here too: deciding *what* and *when* to buy. Purchasing is driven by the demand
forecast and by **MRP**'s planned orders from [Make](#production-planning), then timed against
supplier **lead times** so materials arrive when needed — not so early they pile up as carrying
cost, nor so late they stall production or cause stock-outs. The ongoing disciplines above
(strategic sourcing, supplier development) set this up; inventory targets from
[Storing & inventory](#storing--inventory) tell you how much buffer to carry.

---

# Make

*Manufacture.* Making inventory means **transforming inputs (raw
materials, components) into higher-value outputs**. *Make*, *manufacture*, *produce*, and
*assemble* all point at this same transformation — and it's where much of the supply chain's
value originates.

> In a **distribution** business this pillar is thin: you buy finished goods rather than make
> them, so most of the work lives in [Get](#get) and [Move](#move). Planning still applies,
> though — you plan what to buy and stock.

## Production planning

Planning *what* to make, *how much*, and *when* — keeping production in step with demand. (The
demand side itself — forecasting and demand generation — lives under
[Move → Demand planning](#demand-planning), since it drives stocking and distribution.)

- **S&OP (Sales & Operations Planning)** — the recurring cross-functional cycle that reconciles
  realistic demand targets against supply capacity and constraints, so sales doesn't promise
  what production can't deliver. Coordinates capacity, inventory, production scheduling,
  resource allocation, procurement, and risk. Aggregate strategies: *level production* (steady
  output), *chase demand* (flex output to match), or *inventory buffers*.
- **Master schedule** — the master production schedule (what / how much / when), validated
  against capacity and materials; uses *time fences* to lock the near term.
- **MRP (Material Requirements Planning)** — explodes the master schedule against the
  **Bill of Materials (BOM)** and inventory records to generate planned orders — which drive
  purchasing back in [Get](#procurement-planning). *Lot sizing* sets batch sizes.
- **CRP (Capacity Requirements Planning)** — the reality check: confirms you actually have the
  capacity (equipment, labor) to execute the MRP/master plan, and surfaces bottlenecks.
- **Scheduling / PAC (Production Activity Control)** — how orders hit the floor: *push vs.
  pull*, Just-in-Time (JIT), Theory of Constraints (TOC), and Kanban.

**Product design & life cycle**

- **New-product design** — research & conceptualization → design & engineering (CAD) →
  prototyping → testing & validation.
- **Product life cycle management** — adapt supply strategy as a product moves from launch
  through growth, maturity, and end-of-life.

## Produce

Every manufacturing choice is governed by two levers — **cost** and **lead time** — weighed
against short- and long-term opportunity costs. Four aspects keep the operation healthy:

- **Safety** — minimize environmental risk and long-term exposure; provide PPE.
- **Efficiency** — Output ÷ Input.
- **Capacity & utilization** — every machine and process has a ceiling; Actual ÷ Capacity =
  *utilization*. Aim for high utilization without creating **bottlenecks** that waste time and
  resources.
- **Quality** — deliver real value and cut the cost of poor quality.

The making itself:

- **Manufacturing execution** — assembly, machining, forming, joining (e.g. injection molding).
- **Material handling** — moving and staging materials within the facility.
- **Maintenance & equipment management** — keep equipment running to avoid downtime.
- Production strategy:
  - **Make to stock** — forecast demand, build ahead, and hold inventory.
  - **Make to order** — wait until an order arrives before producing.
  - **Engineer to order** — build each product to a customer's customized needs.
  - **Postponement** (hybrid) — do the long-lead-time work early and hold semi-finished stock,
    then complete final assembly only once a real order lands. Cuts lead time without
    overcommitting inventory.

## Quality

Assure, then verify:

- **Quality assurance (QA)** — *build* quality in: set standards and inspect throughout
  production.
- **Quality control (QC)** — *catch* defects: check finished goods meet specs, with a final
  testing & inspection gate before release.

## Package

Protect, comply, appeal:

- **Packaging** — protect goods in transit, meet regulations, and appeal to customers.
- **Load planning** — plan how freight is arranged and loaded onto the vehicle, then hand off
  to [Move](#move) for dispatch.

---

# Move

*Distribute inventory: store → ship → receive → return.* Logistics plans, executes, and
controls the physical **movement and storage** of goods from origin to destination —
increasingly optimizing for sustainability (efficient routing, fuel economy, waste reduction).
Three jobs: **plan** the moves and paperwork, **implement** them (transport + storage), and
**control** them (tracking, technology, partner coordination). This is usually the densest
pillar — most day-to-day work lives here.

## Logistics players

How these fit together: a **shipper** owns the goods and needs them moved. It can hire a
**carrier** directly, or go through a **broker (3PL)** that arranges carriers on its behalf.

- **Shipper** — the company that owns the products and needs freight moved, also known as the
  **Beneficial Cargo Owner (BCO)**. Often works directly with carriers, but can also use a
  third-party logistics provider (3PL) as a broker between shipper and carrier.
- **Carrier** — a company hired by the shipper that owns the modes of transportation and moves
  freight from one place to another. Large shippers may run their own carrier; without a
  dedicated fleet, a shipper hires a 3PL to provide transportation.
- **Fleet** — the collection of transport vehicles owned or operated by a carrier. A carrier
  may run multiple fleets for different transportation modes.
- **Broker (3PL)** — an intermediary that arranges transportation services between shipper and
  carrier. (Our 3PL broker fills this role here.)

## Branches & facilities

A **branch** is the distribution group's regional hub. It acts as a distribution center for
its region while also handling sales, inventory, and warehouse management. Some branches can
also fabricate — doing their own light manufacturing.

**Two types:** distribution and fabrication.

**Day-to-day roles:**

- **Receiving** — take in incoming shipments from suppliers, manufacturers, or other sources.
- **Storage & inventory management** — hold goods until they're needed to fulfill orders.
- **Order fulfillment** — pick, pack, and ship products to fill customer orders on time.
- **Inventory control** — keep accurate inventory records and track goods moving through the
  facility.
- **Shipping & transportation** — coordinate moving goods to their final destinations.

**Approvals a branch owns:**

- **Freight costs** — verify shipping costs are within budget and match the freight terms
  negotiated in the purchase orders.
- **Shipment arrangements** — have a say in how inbound (from suppliers) and outbound (to
  customers) shipments are arranged, so operations fit each branch's specific needs.
- **Vendor billing** — verify and approve freight charges billed by vendors or carriers, to
  catch duplicate payments and overcharges.

**Facility types** — where goods rest between moves:

- **Distribution center (branch)** — fast throughput; inventory typically held < 48 hours
  before moving on.
- **Warehouse** — general, longer-term storage.
- **Fulfillment center** — geared to pick, pack, and ship customer orders quickly.
- **Return center** — processes returns: inspect, sort, then restock or dispose.

## Buying transportation

Logistics doesn't just move goods — you also have to *buy* the moving. Procurement buys carrier
capacity: for a regular **lane**, you solicit bids (an RFP defining route, volume, frequency,
and service level), choose the **mode** (truck, rail, air, sea), evaluate bids on
price / service / reliability / compliance, **award** a contract, then monitor performance and
re-optimize. Contracted lane rates beat one-off spot quotes; offering a *specific load* to a
contracted carrier is a **tender** (see [Outbound flow](#outbound-flow)). Related levers:
**carrier selection**, **route optimization**, and **freight consolidation** (combining
shipments to cut cost).

**Freight terms & charges.** **Freight terms** on a purchase order are legally binding and
decide *who arranges and pays for* a shipment — so the key question on any inbound load is "who
arranged it?" For example, **Customer Pickup (CPU)** means the supplier only makes the goods
available; getting them is on the buyer (own fleet or a 3PL). When a supplier ships but has the
carrier bill the buyer directly, control over freight cost is lost and duplicate payments get
more likely — so terms are worth managing carefully. Common surprise charges (**accessorials** —
anything beyond standard pickup and delivery):

- **Accessorial** — extra services like liftgate, inside delivery, or storage.
- **Detention** — the driver waits beyond the allotted load/unload time.
- **Reclassification** — the actual **freight class** (set by density, stowability, handling,
  and liability) differs from what was declared, raising the cost.

## Outbound flow

The chronological flow of a shipment: **prepare → dispatch → monitor**. As the shipper, you own
the products and need them moved. Upon receiving the PO, you fulfill the order and arrange
delivery — building loads and tendering them to carriers (often through a broker, who optimizes
carrier selection) to get product from an origin to its destination.

**Prepare**

- **Order processing** — the customer places an order (the PO from [Get](#get)).
- **Load building** — combine orders into a shipment (a "load"), considering weight, volume,
  and destination. The load is then classified as FTL, LTL, or Hotshot (see
  [Transportation reference](#transportation-reference)).
- **Carrier selection (tendering the load)** — pick a carrier based on cost, service level, and
  availability, then **tender** the load and secure their agreement to transport the goods.
  Once the carrier accepts, confirm the remaining delivery details — dates, driver, and route.
- **Prepare items** — pick the items from warehouse inventory, pack them securely for
  transport, and generate and apply shipping labels.
- **Finalize** — schedule the delivery (pickup + drop), assign drivers, finalize route details
  with the carrier, and prepare shipping documents including the **Bill of Lading (BOL)**,
  issued when the shipment is ready for pickup. Then load the goods correctly onto the vehicle.

**Dispatch (execution)**

- **Carrier handoff** — dispatch the truck to the pickup location and hand off the shipment.
  Issue the BOL when the carrier arrives. At this point the load is dispatched — i.e.
  "shipped." (A supplier may send its invoice once the load is dispatched/shipped.)
- **Shipment & order numbers** — when a load is dispatched, our **ERP system** generates a
  shipment number and transmits it to the **broker's TMS**. The TMS creates an order and
  converts it into a **broker order number**. "Third party" means neither the shipper nor the
  receiver is moving the material themselves; if we moved it ourselves, it would go under our
  own fleet.
- **Move** — the carrier's fleet transports the shipment to its destination, following
  established **lanes** — the regular routes carriers use for frequent shipments to keep
  transport predictable and cost-effective.

**Monitor**

- **Track** — use tracking systems for real-time updates on the shipment's location and status.
- **Ensure timeliness** — verify the shipment is sticking to the planned schedule and route.
- **Handle issues** — address delays or route changes and communicate updates to the relevant
  parties.

Across all of this, **fleet management** (vehicles, drivers and DOT compliance, maintenance,
GPS/telematics) and **route & network optimization** (efficient routes + well-placed
distribution centers) keep cost down. Beware *sub-optimization* — local wins that hurt the
network overall; a *regional* supply chain (source and make near the customer) cuts transport
cost and time. The final leg to the customer is the **last mile**, followed by **post-delivery
management**.

## Transportation reference

**Modes of transportation** — ships, trains, trucks, planes. Choosing one balances the
tradeoffs between **cost, speed, and capacity** for the goods at hand. Common truck types:

- **Dry van** — enclosed trailer for palletized or boxed goods.
- **Flatbed** — open deck for long or oversized items.
- **Reefer** (refrigerated) — temperature- and humidity-controlled, for perishables.
- **Chassis** — carries shipping containers.
- **Tanker** — for liquids.
- **Box truck** — versatile medium-sized truck for smaller, protected loads.

**Shipment types**

- **Full Truckload (FTL)** — the load fills the entire truck and goes directly to its
  destination with no stops or intermediaries. Pricing fluctuates a lot.
- **Less Than Truckload (LTL)** — a partial load that shares truck space with others and is
  routed through a series of distribution centers.
- **Hotshot** — urgent, small-scale deliveries within roughly a 150-mile radius, using a
  preferred local carrier that supplements the fleet. Think on-demand: a local move with not a
  lot of material.

**Routes** — a shipment starts at an **origin** and arrives at a **destination**, together the
**O-D pair** (origin-destination pair).

- **Headhaul** — the trip from origin to destination.
- **Backhaul** — the return trip, from destination back to origin.
- **Deadheading** — driving without a load. The trucker isn't paid for it, and it can be risky:
  an empty truck is light enough that strong winds can push it around.
- **Lane** — a specific path carriers use for frequent shipments, making transport predictable
  and cost-effective.

**Units**

- **Handling Unit (HU)** — a single pallet, roll, or box — essentially one lift with the
  forklift.
- **SKU (Stock Keeping Unit)** — a unique identifier for each distinct product, used to track
  inventory accurately. Some performance targets are measured per SKU.

**Bill of Lading (BOL)** — a legal document the shipper issues to the carrier, detailing the
type, quantity, and destination of the goods. It is both a **receipt** for the carrier and a
**contract** between shipper and carrier, and moves through three stages:

- **At pickup** — the shipper hands the BOL to the carrier on pickup, as a receipt showing the
  carrier has taken possession of the shipment.
- **During transit** — the BOL travels with the shipment, carrying its key details: what is
  being shipped, where it's going, and who is shipping it.
- **At delivery** — the receiver signs the BOL to confirm goods arrived in good condition. The
  signed BOL becomes the **Proof of Delivery (POD)** and goes back to the shipper.

## Receiving (inbound)

The mirror image of dispatch — taking goods in the door:

1. **Reception** — when the order arrives, inspect it for quality and accuracy. The receiver
   signs a delivery receipt and the **Proof of Delivery (POD)** — the signed BOL — confirming
   the shipment arrived in good condition. Record the receipt in the company's system.
   - **Live load/unload** — the driver arrives and stays attached to the trailer, waiting while
     it's loaded or unloaded. Often called "bumping the dock" because the trailer is positioned
     against the loading dock the whole time.
   - **Dropped trailer** — the driver drops the trailer in the facility's yard and leaves. The
     facility loads or unloads it later, without the driver present. (A standing arrangement
     for this is a *drop trailer program*.)
2. **Inspection** — at the branch, shipments go through a receiving process where they're
   checked for accuracy (the right quantities were delivered) and quality (materials are free
   from damage).
3. **Approve** — a **Goods Received Note (GRN)** confirms goods were received into the warehouse
   or distribution center. The GRN triggers invoicing: the shipper issues an invoice to the
   buyer once the transaction or delivery is complete. Then **Three-Way Matching** occurs —
   accounts payable matches the PO, the GRN, and the invoice to confirm accuracy and
   completeness. Once approved, the invoice enters the **Accounts Payable (AP) queue**.
4. **Store (put-away)** — the receiver stores the received product and uses inventory management
   to keep it ready for its next distribution to other buyers.

## Demand planning

Demand planning tells the rest of logistics how much to stock and move. (It pairs with
[production planning](#production-planning) under Make, and feeds the stock policies below.)

- **Demand chain** — Marketing (creates awareness) → Sales (closes the purchase) → Customer
  service (ensures satisfaction after). The demand chain *generates* demand; the supply chain
  *satisfies* it.
- **Demand forecasting** — predict future demand from history and market signals.
  *Quantitative* methods (moving averages, exponential smoothing, statistical/ML models) and
  *qualitative* ones (market research, customer feedback). Track forecast error and bias over
  time, then refine.
- **Demand shaping** — actively influence demand with price incentives, promotions, or product
  substitutions.
- **DRP (Distribution Requirements Planning)** — replenishment planning across distribution
  centers to meet that forecast demand.

## Storing & inventory

Inventory can be ~60% of supply-chain cost and is the main lever for balancing supply against
demand. Because it's cash tied up, before buying ask: do we truly need it, can we move and
store it, how long will it last, and what value does it add?

- **Types** — raw materials (inbound) → work-in-process (WIP) → finished goods.
- **Replenishment stock** — **cycle stock** (just-in-time: normal day-to-day use), **safety
  stock** (just-in-case: a buffer against demand spikes and supply delays), and **anticipation
  inventory** (safety stock built ahead of a known event).
- **When to reorder** — at a fixed stock level (**reorder point**) or on a fixed schedule
  (**periodic replenishment**).
- **How much to order** — frequent small orders keep inventory low but raise ordering/transport
  cost; fewer large orders raise cycle stock but cut replenishment cost. **EOQ (Economic Order
  Quantity)** finds the balance.
- **ABC analysis** — prioritize items by value: **A** (few items, most value — tight control),
  **B** (moderate — regular review), **C** (many, least value — loose control).
- **Value erosion** — inventory loses value through *depreciation* (age/wear), *shrinkage*
  (damage, loss, theft), and *obsolescence* (outdated). Carrying cost is often based on the
  company's borrowing/hurdle rate.
- **Coordinate to avoid the bullwhip effect** — small demand swings amplifying upstream. Shared
  forecasts (**CPFR**) and **vendor-managed inventory (VMI)** dampen it; track service with
  metrics like **fill rate**. Guard against disruptions with safety stock, backup suppliers,
  expediting, or substitution.

## Systems

A **TMS** (transportation), **WMS** (warehouse), and **IMS** (inventory) each manage their own
domain, and all integrate with the **ERP** — the single platform that runs day-to-day business
operations.

## Returns (reverse logistics)

- **Return management** — a subset of **reverse logistics** for when there are problems with a
  product, mainly lost or damaged goods and warranty claims. At its core, it's about feedback
  and support to make things right. Returns are processed at a return center (inspect → sort →
  restock or dispose).

---

# Glossary & Quick Reference

Buckets are ordered roughly Get → Make → Move; terms within each are alphabetized.

## People & Players

| Term | Definition |
| --- | --- |
| **3PL (Third-Party Logistics)** | A provider that arranges or handles transportation, acting as a broker between shipper and carrier. |
| **Beneficial Cargo Owner (BCO)** | See *Shipper*. |
| **Branch** | A regional distribution (and sometimes fabrication) hub. |
| **Broker** | An intermediary that arranges transportation services. |
| **Carrier** | A company that owns transport vehicles and moves freight. |
| **Distributor** | Buys from manufacturers, warehouses goods, and sells to wholesalers. |
| **Fleet** | A carrier's collection of transport vehicles. |
| **Manufacturer** | Supplier that turns raw materials into finished products. |
| **Retailer** | The end of the channel; sells to the final customer. |
| **Shipper** | The company that owns the goods and needs them moved (the BCO). |
| **Wholesaler** | Buys in bulk and sells to retailers. |

## Procurement & Sourcing

| Term | Definition |
| --- | --- |
| **Contract management** | Managing procurement contracts so suppliers adhere to terms, conditions, and pricing. |
| **Order placement** | Issuing the purchase order to the chosen vendor. |
| **Order tracking** | Monitoring an order's status through fulfillment. |
| **Payment processing** | Paying the vendor against matched invoices. |
| **Procure-to-Pay (P2P)** | The full procurement cycle from sourcing through ordering and payment. |
| **Quoting** | Estimating cost before committing — e.g. transport cost from distance, load size, road conditions, and urgency. |
| **Spot buy (spot quote)** | A non-contractual, one-off purchase at current market rates — often pricier than contracted terms; used for immediate needs. |
| **Strategic sourcing** | Identifying, evaluating, and contracting suppliers to acquire the best goods and services. |
| **Supplier & carrier negotiations** | Regularly negotiating terms to improve service levels and reduce costs. |
| **Supplier development** | Helping suppliers learn your business and needs; may include process improvement, R&D, faster payments, loans, or partnerships. |
| **Supplier management** | Building and maintaining supplier relationships for reliable supply and quality. |
| **Supplier screening** | Evaluating and shortlisting potential suppliers. |

## Orders, Documents & Billing

| Term | Definition |
| --- | --- |
| **Accounts Payable (AP) queue** | Where approved invoices wait to be paid. |
| **Bill of Lading (BOL)** | Legal receipt and contract between shipper and carrier, detailing the goods. |
| **Goods Received Note (GRN)** | Document confirming goods were received; triggers invoicing. |
| **Proof of Delivery (POD)** | The signed BOL confirming receipt in good condition. |
| **Purchase Order (PO)** | The buyer's order to a vendor, with items, prices, and terms. |
| **Request for Information (RFI)** | An early request to gather information from potential suppliers. |
| **Request for Proposals (RFP)** | A request for supplier bids when no pre-approved vendor fits. |
| **Requisition** | The initial identification of a need for goods or services. |
| **Sales Order (SO)** | The vendor's confirmation that it can fulfill the PO. |
| **Three-Way Matching** | Matching the PO, GRN, and invoice before payment. |

## Planning & Forecasting

| Term | Definition |
| --- | --- |
| **Capacity Requirements Planning (CRP)** | Reality check confirming there's enough capacity to execute the MRP/master plan. |
| **Demand chain** | Marketing → Sales → Customer service; generates demand (vs. the supply chain, which satisfies it). |
| **Demand forecasting** | Predicting future demand from history and market signals. |
| **Demand shaping** | Influencing demand with price incentives, promotions, or substitutions. |
| **Distribution Requirements Planning (DRP)** | Planning inventory replenishment across distribution centers to meet forecast demand. |
| **Lead time** | The time between starting and completing a process (e.g. ordering to delivery). |
| **Master scheduling** | The master production schedule: what to produce, how much, and when. |
| **Material Requirements Planning (MRP)** | Calculating the materials and components needed, and when, to meet the production schedule. |
| **Product life cycle management** | Adapting supply strategy as a product moves from launch through maturity to end-of-life. |
| **S&OP (Sales & Operations Planning)** | The recurring cycle that reconciles demand targets with supply capacity and constraints. |
| **SCOR (Supply Chain Operations Reference)** | Standard model splitting supply chain work into Plan, Source, Make, Deliver, and Return. |
| **Time fence** | A boundary in the schedule beyond which changes are restricted, locking the near term. |

## Production & Manufacturing

| Term | Definition |
| --- | --- |
| **Assembly** | Combining components into finished goods. |
| **Bill of Materials (BOM)** | The list of materials and components needed to make a product. |
| **Engineer to order** | Building each product to a customer's customized needs. |
| **Just-in-Time (JIT)** | A pull system that produces/orders only as needed, minimizing inventory. |
| **Kanban** | A signal-based pull system that triggers production or replenishment on demand. |
| **Load planning** | Planning how freight is arranged and loaded onto a vehicle. |
| **Lot sizing** | Deciding production or order batch sizes. |
| **Make to order** | Waiting until an order arrives before producing. |
| **Make to stock** | Forecasting demand, producing ahead, and holding inventory. |
| **Material handling** | Moving and staging materials within a facility. |
| **Postponement** | Doing long-lead work early, then finishing final assembly only once an order lands. |
| **Production Activity Control (PAC)** | Methods for releasing and sequencing orders on the shop floor (push vs. pull). |
| **Quality assurance (QA)** | Building quality in: setting standards and inspecting throughout production. |
| **Quality control (QC)** | Catching defects: checking finished goods meet specs before release. |
| **Theory of Constraints (TOC)** | Managing throughput by focusing on the system's bottleneck. |
| **Utilization** | Actual output ÷ capacity. |

## Freight & Shipment Types

| Term | Definition |
| --- | --- |
| **Accessorial** | Extra service beyond standard pickup/delivery (liftgate, inside delivery, storage), at added fee. |
| **Box truck** | Versatile medium-sized enclosed truck for smaller, protected loads. |
| **Chassis** | Truck frame that carries shipping containers. |
| **Customer Pickup (CPU)** | Freight term: supplier only makes goods available; the buyer arranges pickup. |
| **Detention fee** | Charge when a driver waits beyond the allotted load/unload time. |
| **Dry van** | Enclosed trailer for palletized or boxed goods. |
| **Flatbed** | Open-deck trailer for long or oversized loads. |
| **Freight** | The goods being moved (a.k.a. cargo, load, shipment). |
| **Freight class** | Rating (density, stowability, handling, liability) used to price freight. |
| **Freight terms** | Legally binding PO terms setting who arranges and pays for shipping. |
| **FTL (Full Truckload)** | A load that fills the truck and ships direct. |
| **Handling Unit (HU)** | One pallet, roll, or box — a single forklift lift. |
| **Hotshot** | An urgent, small, local delivery (~150-mile radius) via a preferred carrier. |
| **Inbound** | Shipments received from suppliers. |
| **LTL (Less Than Truckload)** | A partial load that shares truck space, routed through distribution centers. |
| **Outbound** | Shipments sent to customers. |
| **Reclassification fee** | Charge when actual freight class differs from what was declared. |
| **Reefer** | Refrigerated trailer for perishables (temperature/humidity controlled). |
| **SKU (Stock Keeping Unit)** | A unique identifier for a distinct product. |
| **Tanker** | Trailer for liquid products. |

## Routes & Movement

| Term | Definition |
| --- | --- |
| **Backhaul** | The return trip, from destination back to origin. |
| **Carrier selection** | Choosing carriers on cost, reliability, and service type (FTL, LTL, hotshot). |
| **Deadheading** | Driving without a load — unpaid, and risky in high wind. |
| **Drop trailer program** | Leaving trailers at a site to be loaded/unloaded at convenience. |
| **Fleet management** | Managing a carrier's vehicles, route planning, and drivers. |
| **Freight consolidation** | Combining multiple shipments into one to cut transport cost. |
| **Headhaul** | The trip from origin to destination. |
| **Lane** | A regular route used for frequent shipments. |
| **Lane bidding** | Soliciting and awarding carrier bids for specific lanes across transport modes. |
| **Last mile** | The final leg of delivery to the end customer. |
| **Network optimization** | Designing facility locations and flows to balance cost and service. |
| **O-D pair** | Origin-destination pair: the start and end points of a shipment. |
| **Post-delivery management** | Handling activities after the goods are delivered. |
| **Reverse logistics** | Handling the flow of goods back from the customer (e.g. returns). |
| **Route optimization** | Determining the most efficient routes for transport. |
| **Tendering** | Formally offering a shipment job to a carrier. |

## Inventory & Warehousing

| Term | Definition |
| --- | --- |
| **ABC analysis** | Ranking inventory by value (A/B/C) to set tighter or looser control per tier. |
| **Anticipation inventory** | Stock built ahead of a known upcoming event. |
| **Bullwhip effect** | Small demand swings amplifying into large ones moving upstream. |
| **Carrying (holding) cost** | The cost of holding inventory, often based on the borrowing/hurdle rate. |
| **CPFR (Collaborative Planning, Forecasting & Replenishment)** | Partners sharing forecasts to align supply with demand. |
| **Cycle counting** | Auditing inventory through continuous partial counts. |
| **Cycle stock** | Inventory for normal day-to-day use (just-in-time). |
| **Economic Order Quantity (EOQ)** | The order size that balances ordering/transport cost against holding cost. |
| **Fill rate** | Percentage of ordered items filled from stock on hand. |
| **Finished goods** | Completed products ready for sale. |
| **FIFO / LIFO** | Inventory valuation methods: first-in-first-out / last-in-first-out. |
| **Inventory management** | Storing and tracking goods so they're ready for the next distribution. |
| **Inventory turnover** | How fast inventory is sold and replaced. |
| **Obsolescence** | Loss of inventory value from becoming outdated. |
| **Periodic replenishment** | Reordering on a fixed schedule. |
| **Raw materials** | Inputs awaiting production. |
| **Reorder point** | The stock level that triggers a replenishment order. |
| **Safety stock** | Buffer inventory against demand spikes and supply delays (just-in-case). |
| **Shrinkage** | Inventory loss from damage, theft, or error. |
| **Slotting** | Optimizing where items are stored in a warehouse for efficient picking. |
| **Vendor-Managed Inventory (VMI)** | The supplier manages the buyer's stock levels. |
| **Work-in-process (WIP)** | Partially completed goods still in production. |

## Systems & Technology

| Term | Definition |
| --- | --- |
| **ERP (Enterprise Resource Planning)** | Single platform running day-to-day business operations; integrates the others. |
| **IMS (Inventory Management System)** | Tracks stock levels and generates reorder alerts. |
| **TMS (Transportation Management System)** | Manages transport: route optimization, shipment tracking, carrier relationships. |
| **WMS (Warehouse Management System)** | Manages storage and movement of goods within a warehouse or distribution center. |
