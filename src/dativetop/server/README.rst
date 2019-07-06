================================================================================
  DativeTop Server
================================================================================

Architecture
================================================================================

1. Append-Only Log (AOL). See aol.py.

   The one true source of truth. It is an ordered sequence of EAVT quadruples,
   or "quads". Each quad has a hash, which is computed from the hash of the
   serialized quad and the hash of the immediately preceding quad.

   The AOL is logically monotonic. That is, it only ever grows. This allows us
   to stay CALM and ensure Consistency by building on Logical Monotonicity.

2. Domain Entities. See domain.py:

   - OLDInstance

     - required attributes:

       - slug (str, unique identifier, e.g., "oka")
       - name (str, human readable name, e.g., "Okanagan")
       - url (str, URL, typically the slug suffixed to the URL of a local OLD
         web service)
       - leader (str, URL, the URL of an external OLD instance that this OLD
         instance follows and syncs with)
       - state (str, forced choice, one of "synced", "syncing", or "not in sync", 
       - auto-sync? (bool, setting indicates whether DativeTop should
         continuously and automatically keep this local OLDInstance in sync
         with its leader.

   - DativeApp

     - required attributes:

       - url (str, URL, the local URL where the DativeApp is being served)

   - OLDService

     - required attributes:

       - url (str, URL, the local URL where the OLD service is being served)
