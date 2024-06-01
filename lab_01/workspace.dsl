workspace "delivery Service" {
    name "delivery Service"

    !identifiers hierarchical


    model {

        properties { 
            structurizr.groupSeparator "/"
        }

        user = person "User"


        delivery_system = softwareSystem "delivery Service" {
            description "delivery service software system"

            
            user_service = container "User Service" {
                description "User management service"
            }   

            delivery_service = container "delivery Service" {
                description "Service for creating and tracking deliveryies"
            } 
            
            parcel_service = container "Post Service" {
                description "Service for processing and packaging shipments"
            } 
            
            group "Databases" {
                user_database = container "User Database" {
                    description "Database for storing user data"
                    technology "PostgreSQL"
                    tags "database"
                }

                delivery_database = container "delivery Database" {
                    description "Database for storing delivery data"
                    technology "MongoDB"
                    tags "database"
                    delievery_collection = component "Deliveries collection"{
                        tags "database"
                    }
                    parcels_collection = component "Posts collection"{
                        tags "database"
                    }
                }

                delivery_database -> user_database "Relation between users and shipments"

            }
            
            user -> user_service "User registration and authorization"
            user -> delivery_service "Getting and updating delivery information, creating shipments"

            user_service -> user_database "User data" 
            
            parcel_service -> delivery_database.parcels_collection "Storing and retrieving shipment information"            

            delivery_service -> user_service "Information about recipients and senders"
            delivery_service -> delivery_database.delievery_collection "Retrieving and updating delivery data"
            delivery_service -> parcel_service "Adding a information about shipments" 
            
            
        }

        user -> delivery_system "Adding a shipment, Getting and updating delivery information"

    }
    
    views {
        themes default

        properties {
            structurizr.tooltips true
        }

        systemContext delivery_system {
            autoLayout
            include *
        }

        container delivery_system {
            autoLayout
            include *
        }

        dynamic delivery_system "UC01" "Adding a new user" {
            autoLayout
            user -> delivery_system.user_service "Creating a user (POST /user)"
            delivery_system.user_service -> delivery_system.user_database "Saving user data" 
        }

        dynamic delivery_system "UC02" "Searching for a user by login" {
            autoLayout
            delivery_system.delivery_service -> delivery_system.user_service "Searching for a user by login (GET /user)"
            delivery_system.user_service -> delivery_system.user_database "Getting user data"
        }

        dynamic delivery_system "UC03" "Searching for a user by name and surname mask" {
            autoLayout
            
            delivery_system.delivery_service -> delivery_system.user_service "Searching for a user by name and surname mask"
            delivery_system.user_service -> delivery_system.user_database "SQL query to the database"
        }

        dynamic delivery_system "UC04" "Creating a shipment" {
            autoLayout
            user -> delivery_system.delivery_service "Shipment making"
            delivery_system.delivery_service -> delivery_system.user_service "User authorization"
            delivery_system.delivery_service -> delivery_system.delivery_database "Creating a new shipment"
        }

        dynamic delivery_system "UC05" "Getting user shipments" {
            autoLayout
            user -> delivery_system.delivery_service "Getting user shipments"
            delivery_system.delivery_service -> delivery_system.user_service "User authentication"
            delivery_system.delivery_service -> delivery_system.delivery_database "Getting deliveryies"
            delivery_system.delivery_service -> delivery_system.parcel_service "Getting shipment information"
            delivery_system.parcel_service -> delivery_system.delivery_database "Getting shipments"
        }

        dynamic delivery_system "UC06" "Creating a delivery from user to user" {
            autoLayout
         
            user -> delivery_system.delivery_service "Shipment making"
            delivery_system.delivery_service -> delivery_system.delivery_database "Getting deliveryies"
            delivery_system.delivery_service -> delivery_system.user_service "User authorization"
            delivery_system.delivery_service -> delivery_system.user_service "Finding user"
            delivery_system.user_service -> delivery_system.user_database "Finding user"
        }
        
        dynamic delivery_system "UC07" "Getting delivery information by recipient" {
            autoLayout
            
            user -> delivery_system.delivery_service "Viewing delivery information"
            delivery_system.delivery_service -> delivery_system.user_service "User authorization"
            delivery_system.delivery_service -> delivery_system.user_service "Request by specific recipient user"
            delivery_system.user_service -> delivery_system.user_database "Finding recipient user"
            delivery_system.delivery_service -> delivery_system.delivery_database "Finding delivery by recipient"
        }
        
        dynamic delivery_system "UC08" "Getting delivery information by sender" {
            autoLayout
            
            user -> delivery_system.delivery_service "Viewing delivery information"
            delivery_system.delivery_service -> delivery_system.user_service "User authorization"
            delivery_system.delivery_service -> delivery_system.user_service "Request by specific sender user"
            delivery_system.user_service -> delivery_system.user_database "Finding sender user"
            delivery_system.delivery_service -> delivery_system.delivery_database "Finding delivery by sender"
        }

        styles {
            element "database" {
                shape cylinder
            }
        }
    }
}